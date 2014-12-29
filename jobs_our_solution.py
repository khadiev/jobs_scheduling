""" Simple solution to the Santa 2014 Kaggle competition evaluation metric. 
This solution takes each toy in turn (in chronological order) and assigns the next
available elf to it. """
__author__ = 'Kamil Khadiev'
__date__ = 'December 14, 2014'

import os
import csv
import math
import heapq
import time
import datetime
# import bintrees

from jobs_naivesolution.toy import Toy
from jobs_naivesolution.elf import Elf
from jobs_naivesolution.hours import Hours
from jobs_naivesolution.rbtree_bag import RBTreeBag

# ========================================================================== #

def create_elves(NUM_ELVES):
    """ Elves are stored in a sorted list using heapq to maintain their order by next available time.
    List elements are a tuple of (next_available_time, elf object)
    :return: list of elves
    """
    list_elves = []
    for i in range(1, NUM_ELVES+1):
        elf = Elf(i)
        heapq.heappush(list_elves, (elf.next_available_time, elf))
    return list_elves


def assign_elf_to_toy(input_time, current_elf, current_toy, hrs):
    """ Given a toy, assigns the next elf to the toy. Computes the elf's updated rating,
    applies the rest period (if any), and sets the next available time.
    :param input_time: list of tuples (next_available_time, elf)
    :param current_elf: elf object
    :param current_toy: toy object
    :param hrs: hours object
    :return: list of elves in order of next available
    """
    start_time = hrs.next_sanctioned_minute(input_time)  # double checks that work starts during sanctioned work hours
    duration = int(math.ceil(current_toy.duration / current_elf.rating))
    sanctioned, unsanctioned = hrs.get_sanctioned_breakdown(start_time, duration)

    if unsanctioned == 0:
        return hrs.next_sanctioned_minute(start_time + duration), duration
    else:
        return hrs.apply_resting_period(start_time + duration, unsanctioned), duration

def assign_toy_to_elf(elf_available_time, current_elf, toy, hrs, wcsv, ref_time):
    work_start_time = elf_available_time
    current_elf.next_available_time, work_duration = \
    assign_elf_to_toy(work_start_time, current_elf, toy, hrs)
    current_elf.update_elf(hrs, toy, work_start_time, work_duration)
    tt = ref_time + datetime.timedelta(seconds=60*work_start_time)
    time_string = " ".join([str(tt.year), str(tt.month), str(tt.day), str(tt.hour), str(tt.minute)])
    wcsv.writerow([toy.id, current_elf.id, time_string, work_duration])

def process_elf(current_elf, toys_simple, elf_available_time, hrs, wcsv, ref_time, elves_for_long_works_left, elves_for_long_works, day_begin_minute, rating_donot_change_time, is_all_toys_comes):
    is_no_avalible_toys = False
    if (current_elf.rating >=3.999):
        try:
            try:
                key, toy = toys_simple.max_item()
                if not is_all_toys_comes and key<10*current_elf.rating*60:
                    key = 0
                    is_no_avalible_toys = True
                    print("heapq.heappush(myelves - 3")
                    heapq.heappush(myelves, (current_elf.next_available_time, current_elf))
                else:
                    assign_toy_to_elf(elf_available_time, current_elf, toy, hrs, wcsv, ref_time)
            except KeyError:
                key = 0
                is_no_avalible_toys = True
                print("heapq.heappush(myelves - 4")
                heapq.heappush(myelves, (current_elf.next_available_time, current_elf))
        except ValueError:
            key = 0
            is_no_avalible_toys = True
            print("heapq.heappush(myelves - 5")
            heapq.heappush(myelves, (current_elf.next_available_time, current_elf))
        if (not is_no_avalible_toys):
            if (elves_for_long_works_left>0):
                print("heapq.heappush(elves_for_long_works - 5")
                heapq.heappush(elves_for_long_works, (current_elf.next_available_time, current_elf))
                elves_for_long_works_left = elves_for_long_works_left - 1
            else:
                print("heapq.heappush(myelves - 6")
                heapq.heappush(myelves, (current_elf.next_available_time, current_elf))

    else:
        time_left = day_begin_minute +hrs.hours_per_day*60 - elf_available_time
        time_left = time_left * current_elf.rating
        try:
            key, toy = toys_simple.floor_item(time_left)
            assign_toy_to_elf(elf_available_time, current_elf, toy, hrs, wcsv, ref_time)
        except KeyError:
            if is_all_toys_comes:
                if elf_available_time <= day_begin_minute:
                    print("heapq.heappush(elves_for_long_works - 6")
                    heapq.heappush(elves_for_long_works, (current_elf.next_available_time, current_elf))
                    return elves_for_long_works_left, is_no_avalible_toys
            else:
                key = 0
                is_no_avalible_toys = True
        print("heapq.heappush(myelves - 7")
        heapq.heappush(myelves, (current_elf.next_available_time, current_elf))
    return elves_for_long_works_left, is_no_avalible_toys

def get_next_elf(elves_for_long_works, myelves):
    elf_available_time1, current_elf1 = heapq.heappop(elves_for_long_works)
    elf_available_time2, current_elf2 = heapq.heappop(myelves)
    is_long = elf_available_time1<elf_available_time2
    if is_long:
        elf_available_time, current_elf = elf_available_time1, current_elf1
        print("heapq.heappush(myelves - 8")
        heapq.heappush(myelves, (current_elf2.next_available_time, current_elf2))
    else:
        elf_available_time, current_elf = elf_available_time2, current_elf2
        print("heapq.heappush(elves_for_long_works - 1")
        heapq.heappush(elves_for_long_works, (current_elf1.next_available_time, current_elf1))

    return elf_available_time, current_elf, is_long



def solution_firstAvailableElf(toy_file, soln_file, myelves, battle_group_size):
    """ Creates a simple solution where the next available elf is assigned a toy. Elves do not start
    work outside of sanctioned hours.
    :param toy_file: filename for toys file (input)
    :param soln_file: filename for solution file (output)
    :param myelves: list of elves in a priority queue ordered by next available time
    :return:
    """

    hrs = Hours()
    ref_time = datetime.datetime(2014, 1, 1, 0, 0)
    rating_donot_change_time = 2848
    row_count = 0
    # toys = bintrees.RBTree()
    toys_simple = RBTreeBag()
    elves_for_long_works = list()
    elves_for_long_works_left = len(myelves) - battle_group_size






    with open(toy_file, 'r') as f:
        toysfile = csv.reader(f)
        next(toysfile)  # header row

        with open(soln_file, 'w') as w:
            wcsv = csv.writer(w)
            wcsv.writerow(['ToyId', 'ElfId', 'StartTime', 'Duration'])
            step = 0
            current_minute = 0
            current_day_minute = hrs.day_start
            day_begin_minute = hrs.day_start
            is_day = False

            previouse_toy = None



            for row in toysfile:
                current_toy = Toy(row[0], row[1], row[2])

                step = step + 1
                elf_available_time, current_elf = heapq.heappop(myelves)
                print("heapq.heappop(myelves)<<<<<<<<<<<")
                if (elf_available_time>=current_toy.arrival_minute):
                    print("heapq.heappush(myelves - 1")
                    heapq.heappush(myelves, (current_elf.next_available_time, current_elf))
                else:
                    while (elf_available_time<current_toy.arrival_minute):
                        day_begin_minute = hrs.get_day_begin_minute(elf_available_time, day_begin_minute)
                        elves_for_long_works_left, is_no_avalible_toys = process_elf(current_elf, toys_simple, elf_available_time, hrs, wcsv, ref_time, elves_for_long_works_left, elves_for_long_works, day_begin_minute, rating_donot_change_time, False)
                        if (is_no_avalible_toys):
                            break
                        elf_available_time, current_elf = heapq.heappop(myelves)
                        print("heapq.heappop(myelves)<<<<<<<<<<<")
                    if elf_available_time>=current_toy.arrival_minute:
                        print("heapq.heappush(myelves - 2")
                        heapq.heappush(myelves, (current_elf.next_available_time, current_elf))
                if (len(elves_for_long_works)>0):
                    elf_available_time, current_elf = heapq.heappop(elves_for_long_works)
                    print("heapq.heappop(elves_for_long_works)<<<<<<<<<<<")
                    while (elf_available_time<current_toy.arrival_minute):
                        if (toys_simple.length()>0):
                            try:
                                key, toy = toys_simple.max_item()
                                if (toy.duration>rating_donot_change_time + 1):
                                    toys_simple.insert(toy.duration, toy)
                                    try:
                                        key, toy = toys_simple.ceiling_item(rating_donot_change_time + 1)
                                    except KeyError:

                                        key, toy = toys_simple.max_item()
                            except ValueError:
                                break
                            assign_toy_to_elf(elf_available_time, current_elf, toy, hrs, wcsv, ref_time)
                            print("heapq.heappush(elves_for_long_works - 2")
                            heapq.heappush(elves_for_long_works, (current_elf.next_available_time, current_elf))
                        else:
                            print("heapq.heappush(elves_for_long_works - 3")
                            heapq.heappush(elves_for_long_works, (current_elf.next_available_time, current_elf))
                            break
                        elf_available_time, current_elf = heapq.heappop(elves_for_long_works)
                        print("heapq.heappop(elves_for_long_works)<<<<<<<<<<<")







                # toys.insert(current_toy.duration * hrs.minutes_in_year_up + current_toy.arrival_minute, current_toy)
                toys_simple.insert(current_toy.duration, current_toy)




                if step>0 and step % 1000== 0:
                    print("step=",step)




                # if step>1000000:
                #     break
            print("toys_simple.length()=",toys_simple.length()," len(myelves)=",len(myelves)," len(elves_for_long_works)=",len(elves_for_long_works))
            elf_available_time, current_elf, is_long = get_next_elf(elves_for_long_works, myelves)
            while (toys_simple.length()>0):
                if (is_long):
                    try:
                        key, toy = toys_simple.max_item()
                        if (toy.duration>rating_donot_change_time + 1):
                            toys_simple.insert(toy.duration, toy)
                            try:
                                key, toy = toys_simple.ceiling_item(rating_donot_change_time + 1)
                            except KeyError:
                                key, toy = toys_simple.max_item()
                    except ValueError:
                        break
                    assign_toy_to_elf(elf_available_time, current_elf, toy, hrs, wcsv, ref_time)
                    print("heapq.heappush(elves_for_long_works - 4")
                    heapq.heappush(elves_for_long_works, (current_elf.next_available_time, current_elf))
                else:
                    day_begin_minute = hrs.get_day_begin_minute(elf_available_time)
                    elves_for_long_works = process_elf(current_elf, toys_simple, elf_available_time, hrs, wcsv, ref_time, elves_for_long_works_left, elves_for_long_works, day_begin_minute, rating_donot_change_time, True)


                elf_available_time, current_elf, is_long = get_next_elf(elves_for_long_works, myelves)


    print("finish")




# ======================================================================= #
# === MAIN === #

if __name__ == '__main__':

    start = time.time()

    NUM_ELVES = 900

    toy_file = '/Users/airatshayazdanov/IdeaProjects/dataConvertor/data/jobs/toys_rev2.csv'#os.path.join(os.getcwd(), 'toys_rev2.csv')
    soln_file = '/Users/airatshayazdanov/IdeaProjects/dataConvertor/data/jobs/answer.csv'#os.path.join(os.getcwd(), 'sampleSubmission_rev2.csv')

    myelves = create_elves(NUM_ELVES)
    solution_firstAvailableElf(toy_file, soln_file, myelves, 1)

    print ('total runtime = {0}'.format(time.time() - start))