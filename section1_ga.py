import random, time

POPULATION_SIZE = 500

GENES = ""
x = 0

teacherDict = {}
value = ord('A')
with open("teachers_dict.txt", "r") as f:
    for teacher in f.readlines():
        teacherDict[teacher.rstrip()] = chr(value)
        value += 1

# print(teacherDict)

reverseDict = {}
for key, val in teacherDict.items():
    reverseDict[val] = key


class Individual(object):
    '''
    Class representing individual in population
    '''

    # labs_allocated = []

    def __init__(self, chromosome, section):
        self.chromosome = chromosome
        self.fitness = self.cal_fitness()
        self.section100 = section
        self.section200 = teacherDict[self.section100]

    @classmethod
    def create_gnome(self, section):
        '''
        create chromosome or string of genes
        '''
        gnome_len = len(GENES)
        temp = list(GENES)
        
        chromo = [' ' for i in range(54)]

        labs = 0
        with open("lab_timing.txt", 'r') as f:
            i = 0
            for line in f.readlines():
                line = line.rstrip()
                lst = line.split()
                for j in range(len(lst)):
                    if(lst[j] == section):
                        for k in range(3):
                            chromo[i*9 + j*3 + k] = teacherDict[section]
                            labs += 1

                i += 1

        for _ in range(labs):
            temp.remove(' ')

        gnome_len -= labs;

        i = 0
        while(gnome_len):
            if(chromo[i] == ' '):
                idx = random.randint(0, gnome_len - 1)
                chromo[i] = temp.pop(idx)
                gnome_len -= 1
            i += 1

        # if(len(Individual.labs_allocated) == 0):
        #     for i in range(54):
        #         if(chromo[i] == teacherDict[section]):
        #             Individual.labs_allocated.append(i)

        return chromo

    def mate(self):
        '''
        Perform mating and produce new offspring
        '''

        # chromosome for offspring
        child_chromosome = [ch for ch in self.chromosome]

        # for each day
        for day in range(5):
            slot1 = random.randint(day * 9, (day + 1) * 9 - 1)
            slot2 = random.randint((day + 1) * 9, 51)
            if(child_chromosome[slot1] != self.section200 and 
               child_chromosome[slot2] != self.section200):
                # print(child_chromosome[slot1], child_chromosome[slot2])
                temp = child_chromosome[slot1]
                child_chromosome[slot1] = child_chromosome[slot2]
                child_chromosome[slot2] = temp

        for day in range(6):
            day_chromo = child_chromosome[day * 9:(day + 1) * 9]
            if(len(list(filter(lambda x: x != ' ', day_chromo))) == 2):
                sub = []
                for i in range(len(day_chromo)):
                    if(day_chromo[i] != ' '):
                        sub.append(day_chromo[i])
                        day_chromo[i] = ' '

                day_chromo[1] = sub.pop()
                day_chromo[2] = sub.pop()

        # create new Individual(offspring) using
        # generated chromosome for offspring
        return Individual(child_chromosome, self.section100)

    def cal_fitness(self):
        '''
        Calculate fittness score, it is the number of
        characters in string which differ from target
        string.
        '''
        xfitness = 0
        chromo_len = len(self.chromosome)

        if(x == 1):
            print(self.chromosome)

        # saturday last classes
        for i in range(1, 4):
            if(self.chromosome[chromo_len - i] != ' '):
                xfitness += 1

        # for each day
        for day in range(6):
            day_chromo = self.chromosome[day * 9: (day + 1) * 9]

            if(all([chrome == ' ' for chrome in day_chromo])):
                xfitness += 1000
                continue

            # If on that day no slot is free all classes are there then increase the fitness
            if(len(list(filter(lambda x: x != ' ', day_chromo))) == 1):
                xfitness += 500
                continue

            if(len(list(filter(lambda x: x != ' ', day_chromo))) == 2):
                xfitness += 50
                continue

            count = 0
            for i in range(3):
                if(len(list(filter(lambda x: x != ' ', day_chromo[i * 3:(i + 1) * 3]))) == 1):
                    xfitness += 35

            start = 0
            for i in range(9):
                if(day_chromo[i] != ' '):
                    start = i
                    break
            end = 8
            for i in range(8, -1, -1):
                if(day_chromo[i] != ' '):
                    end = i
                    break

            if(start == 0 and end == 8):
                xfitness += 1

            for i in range(start + 1, end):
                if(day_chromo[i] == ' '):
                    xfitness += 50

            total = end - start + 1
            m = total - len(set(day_chromo[start:end + 1]))

            if(x == 1):
                print(m)

            xfitness += (2 ** m)

        return xfitness

    def badChromo(self):
        for i in range(6):
            day_chromo = self.chromosome[i * 9:(i + 1) * 9]
            if(len(list(filter(lambda x: x != ' ', day_chromo))) == 2):
                idxes = []
                for i in range(len(day_chromo)):
                    if(day_chromo[i] != ' '):
                        idxes.append(i)

                if(idxes[1] - idxes[0] > 1):
                    return True

        return False


def convertToDict(teachers):
    global value, teacherDict, reverseDict
    s = ""
    for teacher in teachers:
        if(not teacherDict.get(teacher)):
            with open("teachers_dict.txt", "a") as f:
                f.write(teacher + "\n")
                teacherDict[teacher] = chr(value)
                reverseDict[chr(value)] = teacher
                value += 1
        s += teacherDict[teacher]
    return s


class TEMPLATE(object):

    def __init__(self, section, teachers, credits):
        self.section = section
        self.teachers = teachers
        self.teacher_count = len(teachers)
        self.credits = credits

        global GENES
        GENES = ""
        self.template1 = convertToDict(self.teachers)

        for temp, cred in zip(self.template1, self.credits):
            GENES += (temp * cred)

        GENES += " " * (51 - len(GENES))

    def calculateSectionTimeTable(self):
        
        generation = 1

        found = False
        population = []

        # create initial population
        for _ in range(POPULATION_SIZE):
            gnome = Individual.create_gnome(self.section)
            population.append(Individual(gnome, self.section))

        max_iterations = 200
        while(not found and max_iterations):

            # sort the population in increasing order of fitness score
            population = sorted(population, key=lambda x: x.fitness)

            # if the individual having lowest fitness score ie.
            # 0 then we know that we have reached to the target
            # and break the loop
            if population[0].fitness <= 6:
                found = True
                break

            # Otherwise generate new offsprings for new generation
            new_generation = []

            # Perform Elitism, that mean 10% of fittest population
            # goes to the next generation
            s = int((10 * POPULATION_SIZE) / 100)
            new_generation.extend(population[:s])

            if(generation > 50 and new_generation[0].badChromo()):
                return -1, -1

            # From 50% of fittest population, Individuals
            # will mate to produce offspring
            s = int((90 * POPULATION_SIZE) / 100)
            for _ in range(s):
                parent1 = random.choice(population[:50])
                child = parent1.mate()
                new_generation.append(child)

            population = new_generation

            # print(f"Generation: {generation}\tString: {''.join(population[0].chromosome)}\tFitness: {population[0].fitness}")

            generation += 1
            max_iterations -= 1

        # population = sorted(population, key=lambda x: x.fitness)
        # print(f"Generation: {generation}\tString: {''.join(population[0].chromosome)}\tFitness: {population[0].fitness}")
        # print(generation)

        return population[0].chromosome, population[0].fitness

    def reverse_dictionary(self, lst):
        new_lst = []
        for i in range(len(lst)):
            new_lst.append(reverseDict.get(lst[i], "-1"))
        return new_lst


def main():
    global GENES
    start = time.time()
    # n = int(input("Enter number of teachers: "))
    n = 6
    teachers = ['NF', 'GM', 'VV', 'ARB', 'HCV', 'SB', 'ENV']
    credits = [4, 4, 4, 4, 4, 4, 2]
    # print("Enter teacher names: ")
    # for _ in range(n):
    #     teacher = input()
    #     teachers.append(teacher.upper())
    template2 = convertToDict(teachers)

    # print(template)

    for temp, cred in zip(template2, credits):
        GENES += (temp * cred)

    GENES += " " * (51 - len(GENES))

    generation = 1

    found = False
    population = []

    # create initial population
    for _ in range(POPULATION_SIZE):
        gnome = Individual.create_gnome('3A')
        population.append(Individual(gnome, '3A'))

    max_iterations = 200
    while(not found and max_iterations):

        # sort the population in increasing order of fitness score
        population = sorted(population, key=lambda x: x.fitness)

        # if the individual having lowest fitness score ie.
        # 0 then we know that we have reached to the target
        # and break the loop
        if population[0].fitness <= 6:
            found = True
            break

        # Otherwise generate new offsprings for new generation
        new_generation = []

        # Perform Elitism, that mean 10% of fittest population
        # goes to the next generation
        s = int((10 * POPULATION_SIZE) / 100)
        new_generation.extend(population[:s])

        # From 50% of fittest population, Individuals
        # will mate to produce offspring
        s = int((90 * POPULATION_SIZE) / 100)
        for _ in range(s):
            parent1 = random.choice(population[:50])
            child = parent1.mate()
            new_generation.append(child)

        population = new_generation

        # print(f"Generation: {generation}\tString: {''.join(population[0].chromosome)}\tFitness: {population[0].fitness}")

        generation += 1
        max_iterations -= 1

    # population = sorted(population, key=lambda x: x.fitness)
    # print(f"Generation: {generation}\tString: {''.join(population[0].chromosome)}\tFitness: {population[0].fitness}")

    time_table = population[0].chromosome
    for i in range(6):
        for j in range(9):
            print(reverseDict.get(time_table[i * 9 + j], "-1").center(5), end="")
        print()

    print(time.time()-start)

    # testing tool
    # global x
    # x = 1
    # z = Individual(population[0].chromosome)


if __name__ == '__main__':
    main()
