def start(file):
    return file.read().split("\n\n")[:-1]


days_of_players = {
    "Monday": [],
    "Tuesday": [],
    "Wednesday": [],
    "Thursday": [],
    "Friday": [],
    "Saturday": [],
    "Sunday": [],
}


class Player:
    def __init__(self, informational_paragraph):
        lines = informational_paragraph.split("\n")
        lines = [info.split(": ")[1] for info in lines]

        self.name = lines[0]
        self.guild = lines[1]
        self.days = lines[2].split(", ")
        self.times = [int(value) for value in lines[3].split(", ")]
        self.roles = lines[4].split(", ")
        if self.days == ['All']:
            self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.role = None

    def __repr__(self):
        return str(self.name) + " (" + str(self.role) + ")"

    def player_tester(self):
        return str(self.name) + " on days " + str(self.days)

    def between(self, value):
        return self.times[0] <= value <= self.max_time()

    def max_time(self):
        max_time = self.times[1]
        if self.times[1] < self.times[0]:
            max_time += 24
        return max_time


def set_members(file, guild_id):
    members = []
    paragraph_array = start(file)
    for paragraphs in paragraph_array:
        print("appending...")
        members.append(Player(paragraphs))
    print([member for member in members if int(member.guild) == guild_id])
    return [member for member in members if int(member.guild) == guild_id]


def create_party(day, time, members):
    member_list = [member for member in members if (day in member.days and member.between(time))]
    member_list = sorted(member_list, key=lambda mem: len(mem.roles))

    if len(member_list) == 0:
        return []

    most_roles = len(max(member_list, key=lambda mem: len(mem.roles)).roles)
    party = [None] * 4
    length = 0

    for i in range(most_roles):
        for member in member_list:
            if len(member.roles) <= i:
                member_list.remove(member)
                break
            elif member.roles[i] == "Tank" and party[0] is None and member.roles[i] not in party:
                party[0] = [member, member.roles[i]]
            elif member.roles[i] == "Support" and party[1] is None and member.roles[i] not in party:
                party[1] = [member, member.roles[i]]
            elif member.roles[i] == "DPS" and party[2] is None and member.roles[i] not in party:
                party[2] = [member, member.roles[i]]
            elif member.roles[i] == "DPS" and party[3] is None and member.roles[i] not in party:
                party[3] = [member, member.roles[i]]
    return [party, len([x for x in party if x is not None])]


def align(members):
    best_party, best_length = [], 0
    for day in days_of_players:
        for time in range(24):
            new_party = create_party(day, time + 1, members)
            if new_party != []:
                new_length = new_party[1]
                new_party = new_party[0]
                if new_length > best_length:
                    best_party = new_party
                    best_length = new_length

    set_party = [member[0] for member in best_party if member is not None]
    roles = [member[1] for member in best_party if member is not None]
    # for i in range(4):
    #     if set_party[i] is not None:
    #         #print(set_party[i])
    #         #print(isinstance(set_party[i], Player))
    #         set_party[i].role = best_party[i]
    #         members.remove(set_party[i])
    for i in range(len(set_party)):
        set_party[i].role = roles[i]
        members.remove(set_party[i])

    return set_party


def create_parties(members):
    party_list = []
    while len(members) > 1:
        party_list.append(align(members))
        print("Aligning,",len(members))
    if len(members) == 1:
        party_list.append(align(members))
        print("Single member")
    return party_list


def reverse_party(party):
    days = [set(person.days) for person in party]
    set_of_days = set(days_of_players.keys())
    day_set = None
    for day in days:
        if day_set is not None:
            set_of_days = set_of_days.intersection(day_set)
        day_set = day

    min_hour = -1
    max_hour = 1000
    for person in party:
        player_max = person.max_time()
        if person.times[0] > min_hour:
            min_hour = person.times[0]
        if player_max < max_hour:
            max_hour = person.max_time()
    time_set = [min_hour, max_hour]

    return [day_set, time_set]


def end_file(party_list):
    file = open("results.txt", "w").close()
    file = open("results.txt", "r+")

    print(len(party_list))
    for party in party_list:
        print("Adding party")
        party_details = reverse_party(party)

        days = list(party_details[0])
        file.write("Days: " + str(days).replace("'", "")[1:-1])
        if party_details[1][1] > 24:
            party_details[1][1] += -24
        file.write("\nTimes: " + str(party_details[1][0]) + " -> " + str(party_details[1][1]))
        file.write("\n\t")

        file.write("\n\t".join(map(str, party)))

        file.write("\n\n")
    return file
