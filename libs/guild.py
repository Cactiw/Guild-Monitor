

class Guild:

    def __init__(self, guild_id, guild_castle, guild_tag, guild_name, guild_lvl, guild_glory, guild_num_players):
        self.id = guild_id
        self.castle = guild_castle
        self.tag = guild_tag
        self.name = guild_name
        self.lvl = guild_lvl
        self.glory = guild_glory
        self.num_players = guild_num_players
        self.new_glory = None

    def __eq__(self, other):
        return self.tag == other.tag


class GuildChange:

    def __init__(self, guild_tag, guild_new_glory, end = False, send = True):
        self.tag = guild_tag
        self.glory = guild_new_glory
        self.end = end
        self.send = send
