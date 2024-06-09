import unittest

import ujson

from scripts.cat.cats import Cat
from scripts.cat.nutrition import Nutrition
from scripts.cat.skills import Skill, SkillPath
from scripts.clan import Clan
from scripts.clan_resources.freshkill import FreshkillPile
from scripts.utility import get_alive_clan_queens


class FreshkillPileTest(unittest.TestCase):

    def setUp(self) -> None:
        self.prey_config = None
        with open("resources/prey_config.json", 'r') as read_file:
            self.prey_config = ujson.loads(read_file.read())
        self.AMOUNT = self.prey_config["start_amount"]
        self.PREY_REQUIREMENT = self.prey_config["prey_requirement"]
        self.CONDITION_INCREASE = self.prey_config["condition_increase"]

    def test_add_freshkill(self) -> None:
        # given
        freshkill_pile = FreshkillPile()
        self.assertEqual(freshkill_pile.pile["expires_in_4"], self.AMOUNT)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], 0)

        # then
        freshkill_pile.add_freshkill(1)
        self.assertEqual(freshkill_pile.pile["expires_in_4"], self.AMOUNT + 1)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], 0)

    def test_remove_freshkill(self) -> None:
        # given
        freshkill_pile1 = FreshkillPile()
        freshkill_pile1.pile["expires_in_1"] = 10
        self.assertEqual(freshkill_pile1.pile["expires_in_1"], 10)
        freshkill_pile1.remove_freshkill(5)

        freshkill_pile2 = FreshkillPile()
        freshkill_pile2.remove_freshkill(5, True)

        # then
        self.assertEqual(freshkill_pile1.pile["expires_in_4"], self.AMOUNT)
        self.assertEqual(freshkill_pile1.pile["expires_in_1"], 5)
        self.assertEqual(freshkill_pile2.total_amount, self.AMOUNT - 5)

    def test_time_skip(self) -> None:
        # given
        freshkill_pile = FreshkillPile()
        self.assertEqual(freshkill_pile.pile["expires_in_4"], self.AMOUNT)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], 0)

        # then
        freshkill_pile.time_skip([], [])
        self.assertEqual(freshkill_pile.pile["expires_in_4"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], self.AMOUNT)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], 0)
        freshkill_pile.time_skip([], [])
        self.assertEqual(freshkill_pile.pile["expires_in_4"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], self.AMOUNT)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], 0)
        freshkill_pile.time_skip([], [])
        self.assertEqual(freshkill_pile.pile["expires_in_4"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], self.AMOUNT)
        freshkill_pile.time_skip([], [])
        self.assertEqual(freshkill_pile.pile["expires_in_4"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], 0)

    def test_feed_cats(self) -> None:
        # given
        test_clan = Clan(name="Test",
                         leader=None,
                         deputy=None,
                         medicine_cat=None,
                         biome='Forest',
                         camp_bg=None,
                         game_mode='expanded',
                         starting_members=[],
                         starting_season='Newleaf')
        test_warrior = Cat()
        test_warrior.status = "warrior"
        test_clan.add_cat(test_warrior)

        # then
        self.assertEqual(test_clan.freshkill_pile.total_amount, self.AMOUNT)
        test_clan.freshkill_pile.feed_cats([test_warrior])
        self.assertEqual(test_clan.freshkill_pile.total_amount,
                         self.AMOUNT - self.PREY_REQUIREMENT["warrior"])

    def test_tactic_younger_first(self) -> None:
        # given
        freshkill_pile = FreshkillPile()
        current_amount = self.PREY_REQUIREMENT["warrior"] * 2
        freshkill_pile.pile["expires_in_4"] = current_amount

        youngest_warrior = Cat()
        youngest_warrior.status = "warrior"
        youngest_warrior.moons = 20
        middle_warrior = Cat()
        middle_warrior.status = "warrior"
        middle_warrior.moons = 30
        oldest_warrior = Cat()
        oldest_warrior.status = "warrior"
        oldest_warrior.moons = 40

        freshkill_pile.add_cat_to_nutrition(youngest_warrior)
        freshkill_pile.add_cat_to_nutrition(middle_warrior)
        freshkill_pile.add_cat_to_nutrition(oldest_warrior)
        self.assertEqual(
            freshkill_pile.nutrition_info[youngest_warrior.ID].percentage, 100)
        self.assertEqual(
            freshkill_pile.nutrition_info[middle_warrior.ID].percentage, 100)
        self.assertEqual(
            freshkill_pile.nutrition_info[oldest_warrior.ID].percentage, 100)

        # when
        freshkill_pile.tactic_younger_first(
            [oldest_warrior, middle_warrior, youngest_warrior])

        # then
        self.assertEqual(
            freshkill_pile.nutrition_info[youngest_warrior.ID].percentage, 100)
        self.assertEqual(
            freshkill_pile.nutrition_info[middle_warrior.ID].percentage, 100)
        self.assertNotEqual(
            freshkill_pile.nutrition_info[oldest_warrior.ID].percentage, 100)

    def test_tactic_less_nutrition_first(self) -> None:
        # given
        freshkill_pile = FreshkillPile()
        current_amount = self.PREY_REQUIREMENT["warrior"] * 2
        freshkill_pile.pile["expires_in_4"] = current_amount

        lowest_warrior = Cat()
        lowest_warrior.status = "warrior"
        lowest_warrior.moons = 20
        middle_warrior = Cat()
        middle_warrior.status = "warrior"
        middle_warrior.moons = 30
        highest_warrior = Cat()
        highest_warrior.status = "warrior"
        highest_warrior.moons = 40

        freshkill_pile.add_cat_to_nutrition(lowest_warrior)
        max_score = freshkill_pile.nutrition_info[lowest_warrior.ID].max_score
        give_score = max_score - self.PREY_REQUIREMENT["warrior"]
        freshkill_pile.nutrition_info[lowest_warrior.ID].current_score = give_score

        freshkill_pile.add_cat_to_nutrition(middle_warrior)
        give_score = max_score - (self.PREY_REQUIREMENT["warrior"] / 2)
        freshkill_pile.nutrition_info[middle_warrior.ID].current_score = give_score

        freshkill_pile.add_cat_to_nutrition(highest_warrior)
        self.assertLessEqual(
            freshkill_pile.nutrition_info[lowest_warrior.ID].percentage, 70)
        self.assertLessEqual(
            freshkill_pile.nutrition_info[middle_warrior.ID].percentage, 90)
        self.assertEqual(
            freshkill_pile.nutrition_info[highest_warrior.ID].percentage, 100)

        # when
        living_cats = [highest_warrior, middle_warrior, lowest_warrior]
        freshkill_pile.living_cats = living_cats
        freshkill_pile.tactic_less_nutrition_first(living_cats)

        # then
        self.assertEqual(freshkill_pile.total_amount, 0)
        self.assertGreaterEqual(
            freshkill_pile.nutrition_info[lowest_warrior.ID].percentage, 60)
        self.assertGreaterEqual(
            freshkill_pile.nutrition_info[middle_warrior.ID].percentage, 80)
        self.assertLess(
            freshkill_pile.nutrition_info[highest_warrior.ID].percentage, 70)

    def test_tactic_sick_injured_first(self) -> None:
        # given
        # young enough kid
        injured_cat = Cat()
        injured_cat.status = "warrior"
        injured_cat.injuries["test_injury"] = {
            "severity": "major"
        }
        sick_cat = Cat()
        sick_cat.status = "warrior"
        sick_cat.illnesses["test_illness"] = {
            "severity": "major"
        }
        healthy_cat = Cat()
        healthy_cat.status = "warrior"

        freshkill_pile = FreshkillPile()
        # be able to feed one queen and some of the warrior
        current_amount = self.PREY_REQUIREMENT["warrior"] * 2
        freshkill_pile.pile["expires_in_4"] = current_amount

        freshkill_pile.add_cat_to_nutrition(injured_cat)
        freshkill_pile.add_cat_to_nutrition(sick_cat)
        freshkill_pile.add_cat_to_nutrition(healthy_cat)
        self.assertEqual(freshkill_pile.nutrition_info[injured_cat.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[sick_cat.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[healthy_cat.ID].percentage, 100)

        # when
        freshkill_pile.tactic_sick_injured_first([healthy_cat, sick_cat, injured_cat])

        # then
        self.assertEqual(freshkill_pile.nutrition_info[injured_cat.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[sick_cat.ID].percentage, 100)
        self.assertLess(freshkill_pile.nutrition_info[healthy_cat.ID].percentage, 70)

    def test_more_experience_first(self) -> None:
        # given
        freshkill_pile = FreshkillPile()
        current_amount = self.PREY_REQUIREMENT["warrior"]
        freshkill_pile.pile["expires_in_4"] = current_amount

        lowest_warrior = Cat()
        lowest_warrior.status = "warrior"
        lowest_warrior.experience = 20
        middle_warrior = Cat()
        middle_warrior.status = "warrior"
        middle_warrior.experience = 30
        highest_warrior = Cat()
        highest_warrior.status = "warrior"
        highest_warrior.experience = 40

        freshkill_pile.add_cat_to_nutrition(lowest_warrior)
        freshkill_pile.add_cat_to_nutrition(middle_warrior)
        freshkill_pile.add_cat_to_nutrition(highest_warrior)
        self.assertEqual(
            freshkill_pile.nutrition_info[lowest_warrior.ID].percentage, 100)
        self.assertEqual(
            freshkill_pile.nutrition_info[middle_warrior.ID].percentage, 100)
        self.assertEqual(
            freshkill_pile.nutrition_info[highest_warrior.ID].percentage, 100)

        # when
        freshkill_pile.tactic_more_experience_first(
            [lowest_warrior, middle_warrior, highest_warrior])

        # then
        # self.assertEqual(freshkill_pile.total_amount,0)
        self.assertLess(
            freshkill_pile.nutrition_info[lowest_warrior.ID].percentage, 70)
        self.assertLess(
            freshkill_pile.nutrition_info[middle_warrior.ID].percentage, 90)
        self.assertEqual(
            freshkill_pile.nutrition_info[highest_warrior.ID].percentage, 100)

    def test_hunter_first(self) -> None:
        # check also different ranks of hunting skill
        # given
        freshkill_pile = FreshkillPile()
        current_amount = self.PREY_REQUIREMENT["warrior"] + (self.PREY_REQUIREMENT["warrior"] / 2)
        freshkill_pile.pile["expires_in_4"] = current_amount

        best_hunter_warrior = Cat()
        best_hunter_warrior.status = "warrior"
        best_hunter_warrior.skills.primary = Skill(SkillPath.HUNTER, 25)
        self.assertEqual(best_hunter_warrior.skills.primary.tier, 3)
        hunter_warrior = Cat()
        hunter_warrior.status = "warrior"
        hunter_warrior.skills.primary = Skill(SkillPath.HUNTER, 0)
        self.assertEqual(hunter_warrior.skills.primary.tier, 1)
        no_hunter_warrior = Cat()
        no_hunter_warrior.status = "warrior"
        no_hunter_warrior.skills.primary = Skill(SkillPath.MEDIATOR, 0, True)

        freshkill_pile.add_cat_to_nutrition(best_hunter_warrior)
        freshkill_pile.add_cat_to_nutrition(hunter_warrior)
        freshkill_pile.add_cat_to_nutrition(no_hunter_warrior)
        self.assertEqual(freshkill_pile.nutrition_info[best_hunter_warrior.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[hunter_warrior.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[no_hunter_warrior.ID].percentage, 100)

        # when
        living_cats = [hunter_warrior, no_hunter_warrior, best_hunter_warrior]
        freshkill_pile.tactic_hunter_first(living_cats)

        # then
        # this hunter should be fed completely
        self.assertEqual(freshkill_pile.nutrition_info[best_hunter_warrior.ID].percentage, 100)
        # this hunter should be fed partially
        self.assertLess(freshkill_pile.nutrition_info[hunter_warrior.ID].percentage, 90)
        self.assertGreater(freshkill_pile.nutrition_info[hunter_warrior.ID].percentage, 70)
        # this cat should not be fed
        self.assertLess(freshkill_pile.nutrition_info[no_hunter_warrior.ID].percentage, 70)

    def test_pregnant_handling(self) -> None:
        # given
        # young enough kid
        pregnant_cat = Cat()
        pregnant_cat.status = "warrior"
        pregnant_cat.injuries["pregnant"] = {
            "severity": "minor"
        }
        cat2 = Cat()
        cat2.status = "warrior"
        cat3 = Cat()
        cat3.status = "warrior"

        freshkill_pile = FreshkillPile()
        # be able to feed one queen and some of the warrior
        current_amount = self.PREY_REQUIREMENT["queen/pregnant"]
        freshkill_pile.pile["expires_in_4"] = current_amount

        freshkill_pile.add_cat_to_nutrition(pregnant_cat)
        freshkill_pile.add_cat_to_nutrition(cat2)
        freshkill_pile.add_cat_to_nutrition(cat3)
        self.assertEqual(freshkill_pile.nutrition_info[pregnant_cat.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[cat2.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[cat3.ID].percentage, 100)

        # when
        freshkill_pile.feed_cats([cat2, cat3, pregnant_cat])

        # then
        self.assertEqual(freshkill_pile.nutrition_info[pregnant_cat.ID].percentage, 100)
        self.assertLess(freshkill_pile.nutrition_info[cat2.ID].percentage, 70)
        self.assertLess(freshkill_pile.nutrition_info[cat3.ID].percentage, 70)

    def test_sick_handling(self) -> None:
        # given
        # one injured, one sick & 1 healthy cat
        injured_cat = Cat()
        injured_cat.status = "warrior"
        injured_cat.injuries["claw-wound"] = {
            "severity": "major"
        }
        sick_cat = Cat()
        sick_cat.status = "warrior"
        sick_cat.illnesses["diarrhea"] = {
            "severity": "major"
        }
        healthy_cat = Cat()
        healthy_cat.status = "warrior"

        freshkill_pile = FreshkillPile()
        # with only enough food for 2 warriors
        current_amount = self.PREY_REQUIREMENT["warrior"] * 2
        freshkill_pile.pile["expires_in_4"] = current_amount

        freshkill_pile.add_cat_to_nutrition(injured_cat)
        freshkill_pile.add_cat_to_nutrition(sick_cat)
        freshkill_pile.add_cat_to_nutrition(healthy_cat)
        self.assertEqual(freshkill_pile.nutrition_info[injured_cat.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[sick_cat.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[healthy_cat.ID].percentage, 100)

        # when
        freshkill_pile.feed_cats([sick_cat, injured_cat, healthy_cat])

        # then
        # ensure the injured and sick cats got fed
        self.assertEqual(freshkill_pile.nutrition_info[injured_cat.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[sick_cat.ID].percentage, 100)
        self.assertLess(freshkill_pile.nutrition_info[healthy_cat.ID].percentage, 70)


class FreshkillPilePregnancyTest(unittest.TestCase):

    def setUp(self) -> None:
        self.prey_config = None
        with open("resources/prey_config.json", 'r') as read_file:
            self.prey_config = ujson.loads(read_file.read())
        self.AMOUNT = self.prey_config["start_amount"]
        self.PREY_REQUIREMENT = self.prey_config["prey_requirement"]
        self.CONDITION_INCREASE = self.prey_config["condition_increase"]

    def test_queen_both_parents(self) -> None:
        # given
        # young enough kid
        mother = Cat()
        mother.gender = "female"
        mother.status = "warrior"
        father = Cat()
        father.gender = "male"
        father.status = "warrior"
        kid = Cat()
        kid.status = "kitten"
        kid.moons = 2
        kid.parent1 = father
        kid.parent2 = mother

        no_parent = Cat()
        no_parent.status = "warrior"

        freshkill_pile = FreshkillPile()
        # be able to feed one queen and some of the warrior
        current_amount = self.PREY_REQUIREMENT["queen/pregnant"] + (self.PREY_REQUIREMENT["warrior"] / 2)
        freshkill_pile.pile["expires_in_4"] = current_amount

        self.assertEqual(kid.nutrition.percentage, 100)
        self.assertEqual(mother.nutrition.percentage, 100)
        self.assertEqual(father.nutrition.percentage, 100)
        self.assertEqual(no_parent.nutrition.percentage, 100)

        # when
        living_cats = [no_parent, father, kid, mother]
        self.assertEqual([mother.ID], list(get_alive_clan_queens(living_cats)[0].keys()))

        freshkill_pile.feed_cats(living_cats, False)

        # then
        self.assertEqual(kid.nutrition.percentage, 100)
        self.assertEqual(mother.nutrition.percentage, 100)
        self.assertLess(no_parent.nutrition.percentage, 90)
        self.assertGreater(no_parent.nutrition.percentage, 70)
        self.assertLess(father.nutrition.percentage, 70)

    def test_queen_female_only(self) -> None:
        # given
        # young enough kid
        mother = Cat()
        mother.gender = "female"
        mother.status = "warrior"

        kid = Cat()
        kid.status = "kitten"
        kid.moons = 2

        kid.parent1 = mother

        no_parent = Cat()
        no_parent.status = "warrior"

        freshkill_pile = FreshkillPile()
        # be able to feed one queen and some of the warrior
        current_amount = self.PREY_REQUIREMENT["queen/pregnant"] + (self.PREY_REQUIREMENT["warrior"] / 2)
        freshkill_pile.pile["expires_in_4"] = current_amount

        self.assertEqual(kid.nutrition.percentage, 100)
        self.assertEqual(mother.nutrition.percentage, 100)
        self.assertEqual(no_parent.nutrition.percentage, 100)

        # when
        living_cats = [no_parent, kid, mother]
        self.assertEqual([mother.ID], list(get_alive_clan_queens(living_cats)[0].keys()))
        freshkill_pile.tactic_status(living_cats)

        # then
        self.assertEqual(freshkill_pile.nutrition_info[kid.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[mother.ID].percentage, 100)
        self.assertLess(freshkill_pile.nutrition_info[no_parent.ID].percentage, 90)
        self.assertGreater(freshkill_pile.nutrition_info[no_parent.ID].percentage, 70)

    def test_queen_male_only(self):
        # given
        # young enough kid
        father = Cat()
        father.gender = "male"
        father.status = "warrior"
        kid = Cat()
        kid.status = "kitten"
        kid.moons = 2
        kid.parent1 = father

        no_parent = Cat()
        no_parent.status = "warrior"

        freshkill_pile = FreshkillPile()

        # be able to feed two warriors and a kitten
        current_amount = (self.PREY_REQUIREMENT["warrior"] * 2) + self.PREY_REQUIREMENT["kitten"]
        freshkill_pile.pile["expires_in_4"] = current_amount

        self.assertEqual(kid.nutrition.percentage, 100)
        self.assertEqual(father.nutrition.percentage, 100)
        self.assertEqual(no_parent.nutrition.percentage, 100)

        # when
        living_cats = [no_parent, kid, father]
        self.assertNotEqual([father.ID], list(get_alive_clan_queens(living_cats)[0].keys()))
        freshkill_pile.tactic_status(living_cats)

        # then
        self.assertEqual(kid.nutrition.percentage, 100)
        self.assertEqual(father.nutrition.percentage, 100)
        self.assertLess(no_parent.nutrition.percentage, 90)
        self.assertGreater(no_parent.nutrition.percentage, 70)


class FreshkillBaseSortTest(unittest.TestCase):
    def setUp(self) -> None:
        self.prey_config = None
        with open("resources/prey_config.json", 'r') as read_file:
            self.prey_config = ujson.loads(read_file.read())
        self.AMOUNT = self.prey_config["start_amount"]
        self.PREY_REQUIREMENT = self.prey_config["prey_requirement"]
        self.CONDITION_INCREASE = self.prey_config["condition_increase"]

    def test_sort_status(self):
        self.newborn1 = Cat(status="newborn")
        self.kitten1 = Cat(status="kitten")
        self.app1 = Cat(status="apprentice")
        self.warrior1 = Cat(status="warrior")
        self.warrior2 = Cat(status="warrior")
        self.warrior3 = Cat(status="warrior")
        self.elder1 = Cat(status="elder")

        self.all_cats = [self.newborn1, self.kitten1, self.app1, self.warrior1, self.warrior2, self.warrior3,
                         self.elder1]

        correct_order = [self.newborn1, self.kitten1,
                         self.elder1, self.app1,
                         self.warrior1, self.warrior2,
                         self.warrior3]

        self.assertEqual(FreshkillPile.sort_cats(self.all_cats, ["status"]), correct_order)

    def test_sort_moons(self):
        self.newborn1 = Cat(moons=0)
        self.kitten1 = Cat(moons=1)
        self.app1 = Cat(moons=7)
        self.warrior1 = Cat(moons=12)
        self.warrior2 = Cat(moons=50)
        self.warrior3 = Cat(moons=70)
        self.elder1 = Cat(moons=121)

        self.all_cats = [self.newborn1, self.kitten1, self.app1, self.warrior1, self.warrior2, self.warrior3,
                         self.elder1]

        correct_order = [self.newborn1, self.kitten1,
                         self.app1, self.warrior1,
                         self.warrior2, self.warrior3,
                         self.elder1]

        self.assertEqual(FreshkillPile.sort_cats(self.all_cats, ["moons"]), correct_order)

    def test_sort_nutrition(self):
        self.newborn1 = Cat(status="newborn", moons=0, nutrition=Nutrition("newborn"))
        self.kitten1 = Cat(status="kitten", moons=1, nutrition=Nutrition("kitten"))
        self.app1 = Cat(status="apprentice", moons=7, nutrition=Nutrition("apprentice"))
        self.warrior1 = Cat(status="warrior", moons=12, nutrition=Nutrition("warrior"))
        self.warrior2 = Cat(status="warrior", moons=50, nutrition=Nutrition("warrior"))
        self.warrior3 = Cat(status="warrior", moons=70, nutrition=Nutrition("warrior"))
        self.elder1 = Cat(status="elder", moons=121, nutrition=Nutrition("elder"))

        self.all_cats = [self.newborn1, self.kitten1, self.app1, self.warrior1, self.warrior2, self.warrior3,
                         self.elder1]

        Nutrition.update_nutrition(self.all_cats)

        for cat in self.all_cats:
            with self.subTest():
                self.assertEqual(cat.nutrition.percentage, 100)

        self.elder1.nutrition.percentage = 20
        self.warrior1.nutrition.percentage = 80
        self.newborn1.nutrition.percentage = 90

        correct_order = [self.elder1, self.warrior1,
                         self.newborn1, self.kitten1,
                         self.app1, self.warrior2,
                         self.warrior3]

        self.assertEqual(FreshkillPile.sort_cats(self.all_cats, ["nutrition"]), correct_order)

        for cat in self.all_cats:
            cat.nutrition.percentage = 100

    def test_sort_hunter_primary(self):
        warrior1 = Cat(status="warrior")
        warrior2 = Cat(status="warrior")
        warrior3 = Cat(status="warrior")

        all_cats = [warrior1, warrior2, warrior3]

        warrior1.skills.primary = Skill(SkillPath.HUNTER, 25)
        self.assertEqual(warrior1.skills.primary.tier, 3)

        warrior3.skills.primary = Skill(SkillPath.HUNTER, 0)
        self.assertEqual(warrior3.skills.primary.tier, 1)

        correct_order = [warrior1, warrior3, warrior2]

        self.assertEqual(FreshkillPile.sort_cats(all_cats, ["hunter"]), correct_order)

    def test_sort_hunter_secondary(self):
        warrior1 = Cat(status="warrior")
        warrior2 = Cat(status="warrior")
        warrior3 = Cat(status="warrior")

        all_cats = [warrior1, warrior2, warrior3]

        warrior1.skills.secondary = Skill(SkillPath.HUNTER, 25)
        self.assertEqual(warrior1.skills.secondary.tier, 3)

        warrior3.skills.secondary = Skill(SkillPath.HUNTER, 0)
        self.assertEqual(warrior3.skills.secondary.tier, 1)

        correct_order = [warrior1, warrior3, warrior2]

        self.assertEqual(FreshkillPile.sort_cats(all_cats, ["hunter"]), correct_order)

    def test_sort_hunter_mixed(self):
        warrior1 = Cat(status="warrior")
        warrior2 = Cat(status="warrior")
        warrior3 = Cat(status="warrior")

        all_cats = [warrior1, warrior2, warrior3]

        warrior1.skills.primary = Skill(SkillPath.HUNTER, 25)
        self.assertEqual(warrior1.skills.primary.tier, 3)

        warrior3.skills.secondary = Skill(SkillPath.HUNTER, 0)
        self.assertEqual(warrior3.skills.secondary.tier, 1)

        correct_order = [warrior1, warrior3, warrior2]

        self.assertEqual(FreshkillPile.sort_cats(all_cats, ["hunter"]), correct_order)

    def test_sort_multiple(self):
        newborn1 = Cat(status="newborn", moons=0)
        kitten1 = Cat(status="kitten", moons=1)
        app1 = Cat(status="apprentice", moons=7)
        warrior1 = Cat(status="warrior", moons=12)
        warrior2 = Cat(status="warrior", moons=70)
        warrior3 = Cat(status="warrior", moons=50)
        elder1 = Cat(status="elder", moons=121)

        all_cats = [newborn1, app1, warrior1, warrior2, warrior3, elder1]

        correct_order = [newborn1, elder1, app1, warrior1, warrior3, warrior2]

        self.assertEqual(FreshkillPile.sort_cats(all_cats, ["status", "moons"]), correct_order)


class FreshkillBaseSortSickTest(unittest.TestCase):
    def test_sort_sick_one_cat_sickness(self):
        self.cat1 = Cat()
        self.cat2 = Cat()
        self.sick_cat = Cat()

        self.all_cats = [self.cat1, self.cat2, self.sick_cat]

        test_cases = [
            {"name": "diarrhea", "severity": "minor"},
            {"name": "diarrhea", "severity": "major"}
        ]

        for case in test_cases:
            with self.subTest(name=case["name"], severity=case["severity"]):
                self.sick_cat.illnesses[case["name"]] = {
                    "severity": case["severity"]
                }
                correct_order = [self.sick_cat, self.cat1, self.cat2]
                self.assertEqual(FreshkillPile.sort_cats(self.all_cats, ["sick"]), correct_order)
                self.sick_cat.illnesses = {}

    def test_sort_sick_one_cat_multiple_sickness(self):
        self.cat1 = Cat()
        self.cat2 = Cat()
        self.sick_cat = Cat()

        self.all_cats = [self.cat1, self.cat2, self.sick_cat]

        self.sick_cat.illnesses["diarrhea"] = {
            "severity": "major"
        }
        self.sick_cat.illnesses["vomiting"] = {
            "severity": "major"
        }

        self.assertEqual(FreshkillPile.sort_sick(self.sick_cat), 4)

        correct_order = [self.sick_cat, self.cat1, self.cat2]
        self.assertEqual(FreshkillPile.sort_cats(self.all_cats, ["sick"]), correct_order)

    def test_sort_sick_one_cat_multiple_severities(self):
        self.cat1 = Cat()
        self.cat2 = Cat()
        self.sick_cat = Cat()

        self.all_cats = [self.cat1, self.cat2, self.sick_cat]

        self.sick_cat.illnesses["diarrhea"] = {
            "severity": "major"
        }
        self.sick_cat.illnesses["vomiting"] = {
            "severity": "minor"
        }

        self.assertEqual(FreshkillPile.sort_sick(self.sick_cat), 3)

        correct_order = [self.sick_cat, self.cat1, self.cat2]
        self.assertEqual(FreshkillPile.sort_cats(self.all_cats, ["sick"]), correct_order)

    def test_sort_sick_multiple_cats(self):
        self.cat1 = Cat()
        self.sick_cat1 = Cat()
        self.sick_cat2 = Cat()

        self.all_cats = [self.cat1, self.sick_cat1, self.sick_cat2]

        self.sick_cat1.illnesses["diarrhea"] = {
            "severity": "major"
        }
        self.sick_cat2.illnesses["diarrhea"] = {
            "severity": "major"
        }

        correct_order = [self.sick_cat1, self.sick_cat2, self.cat1]

        self.assertEqual(FreshkillPile.sort_cats(self.all_cats, ["sick"]), correct_order)

    def test_sort_sick_multiple_severities(self):
        self.cat1 = Cat()
        self.sick_cat1 = Cat()
        self.sick_cat2 = Cat()

        self.all_cats = [self.cat1, self.sick_cat1, self.sick_cat2]

        self.sick_cat1.illnesses["diarrhea"] = {
            "severity": "minor"
        }
        self.sick_cat2.illnesses["diarrhea"] = {
            "severity": "major"
        }

        correct_order = [self.sick_cat2, self.sick_cat1, self.cat1]
        self.assertEqual(FreshkillPile.sort_cats(self.all_cats, ["sick"]), correct_order)

    def test_sort_sick_one_cat_one_injury(self):
        self.cat1 = Cat()
        self.cat2 = Cat()
        self.sick_cat = Cat()

        self.all_cats = [self.cat1, self.cat2, self.sick_cat]

        test_cases = [
            {"name": "bruises", "severity": "minor"},
            {"name": "broken bone", "severity": "major"}
        ]

        for case in test_cases:
            with self.subTest(name=case["name"], severity=case["severity"]):
                self.sick_cat.injuries[case["name"]] = {
                    "severity": case["severity"]
                }
                correct_order = [self.sick_cat, self.cat1, self.cat2]
                self.assertEqual(FreshkillPile.sort_cats(self.all_cats, ["sick"]), correct_order)
                self.sick_cat.illnesses = {}

    def test_sort_sick_one_cat_multiple_injuries(self):
        self.cat1 = Cat()
        self.cat2 = Cat()
        self.sick_cat = Cat()

        self.all_cats = [self.cat1, self.cat2, self.sick_cat]

        self.sick_cat.injuries["broken bone"] = {
            "severity": "major"
        }
        self.sick_cat.injuries["bruises"] = {
            "severity": "major"
        }

        self.assertEqual(FreshkillPile.sort_sick(self.sick_cat), 4)

        correct_order = [self.sick_cat, self.cat1, self.cat2]
        self.assertEqual(FreshkillPile.sort_cats(self.all_cats, ["sick"]), correct_order)

    def test_sort_sick_one_cat_injury_multiple_severities(self):
        self.cat1 = Cat()
        self.cat2 = Cat()
        self.sick_cat = Cat()

        self.all_cats = [self.cat1, self.cat2, self.sick_cat]

        self.sick_cat.injuries["broken bone"] = {
            "severity": "major"
        }
        self.sick_cat.injuries["bruises"] = {
            "severity": "minor"
        }

        self.assertEqual(FreshkillPile.sort_sick(self.sick_cat), 3)

        correct_order = [self.sick_cat, self.cat1, self.cat2]
        self.assertEqual(FreshkillPile.sort_cats(self.all_cats, ["sick"]), correct_order)

    def test_sort_sick_injury_multiple_cats(self):
        self.cat1 = Cat()
        self.sick_cat1 = Cat()
        self.sick_cat2 = Cat()

        self.all_cats = [self.cat1, self.sick_cat1, self.sick_cat2]

        self.sick_cat1.illnesses["broken bone"] = {
            "severity": "major"
        }
        self.sick_cat2.illnesses["broken bone"] = {
            "severity": "major"
        }

        correct_order = [self.sick_cat1, self.sick_cat2, self.cat1]

        self.assertEqual(FreshkillPile.sort_cats(self.all_cats, ["sick"]), correct_order)

    def test_sort_sick_injured_multiple_severities(self):
        self.cat1 = Cat()
        self.sick_cat1 = Cat()
        self.sick_cat2 = Cat()

        self.all_cats = [self.cat1, self.sick_cat1, self.sick_cat2]

        self.sick_cat1.illnesses["bruises"] = {
            "severity": "minor"
        }
        self.sick_cat2.illnesses["broken bone"] = {
            "severity": "major"
        }

        correct_order = [self.sick_cat2, self.sick_cat1, self.cat1]
        self.assertEqual(FreshkillPile.sort_cats(self.all_cats, ["sick"]), correct_order)
