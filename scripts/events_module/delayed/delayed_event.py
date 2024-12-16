from random import choice

from scripts.cat.cats import Cat


class DelayedEvent:
    def __init__(
            self,
            originator_event: str = None,
            type: str = None,
            pool: dict = None,
            amount_of_events: tuple = None,
            moon_delay: tuple = 0,
            involved_cats: dict = None,
    ):
        self.originator_event = originator_event
        self.type = type
        self.pool = pool
        self.amount_of_events = amount_of_events
        self.moon_delay = moon_delay

        self.involved_cats = involved_cats

    def collect_involved_cats(self, cat_dict, delayed_info) -> dict:
        """
        collects involved cats and assigns their roles for the delayed event, then
        returns a dict associating their new role (key) with their cat ID (value)

        :param cat_dict: a dict of cats already present with the parent event of the delayed event. Key should be abbr
        string and value should be cat object.
        :param delayed_info: the delayed_info dict from the parent event
        """
        gathered_cat_dict = {}

        for new_role, cat_involved in delayed_info["involved_cats"].items():
            # grab any cats that need to be newly gathered
            if isinstance(cat_involved, dict):
                gathered_cat_dict[new_role] = self.get_constrained_cat(
                    cat_involved,
                    cat_dict
                )
                continue

            # otherwise, assign already involved cats to their new role within the delayed event
            gathered_cat_dict[new_role] = cat_dict[cat_involved].ID

        return gathered_cat_dict

    def get_constrained_cat(self, constraint_dict, already_involved: dict):
        """
        checks the living clan cat list against constraint_dict to find any eligible cats.
        returns a single cat ID chosen from eligible cats
        """

        # we're just keeping this to living cats within the clan for now, more complexity can come later
        alive_cats = [
            kitty for kitty in Cat.all_cats.values()
            if not kitty.dead
            and not kitty.outside
            and kitty not in already_involved.values()
        ]

        funct_dict = {
            "age": self._check_age,
            "status": self._check_status,
            "skill": self._check_skill,
            "trait": self._check_trait,
            "backstory": self._check_backstory
        }

        allowed_cats = []
        for param in funct_dict:
            allowed_cats = funct_dict[param](alive_cats, constraint_dict["param"])

            # if the list is emptied, break
            if not allowed_cats:
                break

        if not allowed_cats:
            return None

        return choice(allowed_cats).ID

    @staticmethod
    def _check_age(cat_list: list, ages: list) -> list:
        """
        checks cat_list against required ages and returns qualifying cats
        """
        if "any" in ages:
            return cat_list

        return [kitty for kitty in cat_list if kitty.age in ages]

    @staticmethod
    def _check_status(cat_list: list, statuses: list) -> list:
        """
        checks cat_list against required statuses and returns qualifying cats
        """
        if "any" in statuses:
            return cat_list

        return [kitty for kitty in cat_list if kitty.status in statuses]

    @staticmethod
    def _check_skill(cat_list: list, skills: list) -> list:
        """
        checks cat_list against required skills and returns qualifying cats
        """
        removals = []

        for kitty in cat_list:
            has_skill = False
            for _skill in skills:
                split_skill = _skill.split(",")

                if len(split_skill) < 2:
                    print("Cat skill incorrectly formatted", _skill)
                    continue

                if kitty.skills.meets_skill_requirement(split_skill[0], int(split_skill[1])):
                    has_skill = True

            if not has_skill:
                removals.append(kitty)

        return [kitty for kitty in cat_list if kitty not in removals]

    @staticmethod
    def _check_trait(cat_list: list, traits: list) -> list:
        """
        checks cat_list against required traits and returns qualifying cats
        """
        return [kitty for kitty in cat_list if kitty.trait in traits]

    @staticmethod
    def _check_backstory(cat_list: list, backstories: list) -> list:
        """
        checks cat_list against required backstories and returns qualifying cats
        """
        return [kitty for kitty in cat_list if kitty.backstory in backstories]


delayed_event = DelayedEvent()
