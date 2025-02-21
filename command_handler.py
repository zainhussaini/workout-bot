from numpy.lib.histograms import _search_sorted_inclusive
from workout_logger import WorkoutLogger
from tabulate import tabulate
import datetime
import discord
import re


def pretty_delta(date: datetime.datetime, now: datetime.datetime) -> str:
    """Pretty time difference for saying how long ago workout was."""
    # based on https://stackoverflow.com/a/5164027
    diff = now - date
    total_seconds = diff.total_seconds()
    mins, secs = divmod(int(total_seconds), 60)
    hours, mins = divmod(mins, 60)
    days, hours = divmod(hours, 24)
    assert days == diff.days

    if total_seconds < 0:
        return "in the future?"
    elif total_seconds < 10:
        return f"{total_seconds:.2f} seconds ago"
    elif total_seconds < 60:
        return f"{total_seconds:.1f} seconds ago"
    elif total_seconds < 60*60:
        end1 = 's' if mins != 1 else ''
        end2 = 's' if secs != 1 else ''
        return f"{mins} minute{end1} {secs} second{end2} ago"
    elif total_seconds < 24*60*60:
        end1 = 's' if hours != 1 else ''
        end2 = 's' if mins != 1 else ''
        return f"{hours} hour{end1} {mins} minute{end2} ago"
    elif total_seconds < 14*24*60*60:
        end1 = 's' if days != 1 else ''
        end2 = 's' if hours != 1 else ''
        return f"{days} day{end1} {hours} hour{end2} ago"
    elif total_seconds < 60*24*60*60:
        return date.strftime("on %B %-d")
    else:
        return date.strftime("on %B %-d, %Y")


def shorten_name(name: str, length: int = -1) -> str:
    """Removes id portion of name, and if name is still longer than length,
    shortens it with ellipses. If length is None, then don't shorten with ellipses.
    """
    if "#" in name:
        raise Exception("Warning: passed name with '#' in it")
    if length >= 0 and length < 3:
        raise Exception(f"shorten_name requires length >= 3, got {length}")

    if length < 0 or len(name) <= length:
        return name
    else:
        return name[:length-3] + "."*3


class CommandHandler:
    def handle_command(message: discord.Message):
        # remove surrounding white space
        text: str = message.content.strip()
        # only look at commands starting with "!"
        if len(text) == 0 or text[0] != "!":
            return None

        # extract the root of the command (ie. "!point 12" -> "point")
        base_command = text.split(" ")[0][1:]
        if base_command not in COMMAND_MAP:
            # response None indicates that command is ignored
            return None
        function = COMMAND_MAP[base_command]

        # extract args list by seperating out words, ignoring multiple spaces
        args = [a for a in text.split(" ")[1:] if a]

        # the response can indicate that the command worked, or why it failed
        response: str = function(message, args)
        return response

    def _point(message: discord.Message, args: "list[str]") -> str:
        if args:
            if len(args) != 1:
                response = "Command !point only takes up to one argument"
                return response

            # ex. <@!012345678912345678>
            match = re.match(r"\<@!?([0-9]+)>$", args[0])
            if match is None:
                response = "To set points for another member, use @ (ex. !point @WorkoutTrackerBot)"
                return response

            test_id = match.groups()[0]
            member = message.guild.get_member(int(test_id))
            if member is None:
                response = "Could not match this user id to member of this server"
                return response

            id = test_id
            if member.nick is not None:
                name = member.nick
            else:
                name = member.name
        else:
            id = str(message.author.id)
            name = None

        time = datetime.datetime.now().timestamp()
        with WorkoutLogger(message.guild.id) as wl:
            last_workout_date, points = wl.add_workout(id, time)
        if last_workout_date is None:
            if name is None:
                response = "You now have 1 point. Congrats on the first workout!"
            else:
                response = f"{name} now has 1 point. Congrats on the first workout!"
        else:
            now = datetime.datetime.now()
            if name is None:
                response = f"You now have {points} points. Your last workout was {pretty_delta(last_workout_date, now)}."
            else:
                response = f"{name} now has {points} points. Their last workout was {pretty_delta(last_workout_date, now)}."
        return response

    def _loser(message: discord.Message, args: "list[str]") -> str:
        if args:
            if len(args) != 1:
                response = "Command !loser only takes up to one argument"
                return response

            # ex. <@!012345678912345678>
            match = re.match(r"\<@!?([0-9]+)>$", args[0])
            if match is None:
                response = "To set points for another member, use @ (ex. !point @WorkoutTrackerBot)"
                return response

            test_id = match.groups()[0]
            member = message.guild.get_member(int(test_id))
            if member is None:
                response = "Could not match this user id to member of this server"
                return response

            id = test_id
            if member.nick is not None:
                name = member.nick
            else:
                name = member.name
        else:
            id = str(message.author.id)
            name = None

        with WorkoutLogger(message.guild.id) as wl:
            removed_test = wl.remove_last_workout(id)
        if removed_test:
            with WorkoutLogger(message.guild.id) as wl:
                points = wl.get_points(id)
            if points == 0:
                if name is None:
                    response = "You don't have any more points."
                else:
                    response = f"{name} doesn't have any more points."
            elif points == 1:
                if name is None:
                    response = "You have 1 point left."
                else:
                    response = f"{name} has 1 point left."
            else:
                if name is None:
                    response = f"You have {points} points left."
                else:
                    response = f"{name} has {points} points left."
        else:
            if name is None:
                response = "You don't have any points to remove!"
            else:
                response = f"{name} doesn't have any points to remove!"
        return response

    def _scoreboard(message: discord.Message, args: "list[str]") -> str:
        if args:
            response = "Command !scoreboard does not take any arguments"
            return response

        with WorkoutLogger(message.guild.id) as wl:
            sorted_member_ids, member_id_to_points = wl.get_leaderboard()
        if not sorted_member_ids:
            return "Scoreboard is empty!"
        table = []
        headers = ["Rank", "Name", "Points"]
        for i, member_id in enumerate(sorted_member_ids):
            member = message.guild.get_member(int(member_id))
            if member is not None:
                if member.nick is not None:
                    name = member.nick
                else:
                    name = member.name
            else:
                # member not found if someone leaves the channel
                name = "member_not_found"

            points = member_id_to_points[member_id]
            # using 14 because that's lowest screen size report by users
            shortened_name = shorten_name(name, 14)

            # calculate rank so that people with same points have same rank
            if len(table) != 0 and table[-1][2] == points:
                # if previous person's points are the same as yours, don't increase rank
                rank = table[-1][0]
            else:
                rank = i+1

            table.append([rank, shortened_name, points])
        return "```\n" + tabulate(table, headers) + "\n```"

    def _resetscoreboard(message: discord.Message, args: "list[str]") -> str:
        if args:
            response = "Command !resetscoreboard does not take any arguments"
            return response

        if message.author.permissions_in(message.channel).administrator:
            with WorkoutLogger(message.guild.id) as wl:
                wl.reset_leaderboard()
            response = "Scoreboard has been reset!"
            return response
        else:
            response = "You need administrator permissions for that"
            return response

    def _help(message: discord.Message, args: "list[str]"):
        if args:
            response = "Command !help does not take any arguments"
            return response

        help_items = [
            "!point - add a workout for yourself (or @ someone to add a point for them instead)",
            "!loser - remove your last workout (or @ someone to remove their last workout instead)",
            "!scoreboard - show the rankings",
            "!resetscoreboard - clear all workouts",
            "!help - show this help text"
        ]
        return "\n".join(help_items)


COMMAND_MAP = {
    "point": CommandHandler._point,
    "loser": CommandHandler._loser,
    "scoreboard": CommandHandler._scoreboard,
    "resetscoreboard": CommandHandler._resetscoreboard,
    "help": CommandHandler._help,
}
