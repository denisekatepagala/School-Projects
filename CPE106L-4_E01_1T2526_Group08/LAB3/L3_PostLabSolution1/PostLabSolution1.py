class Student(object):
    """Represents a student."""

    def __init__(self, name, number):
        """All scores are initially 0."""
        self.name = name
        self.scores = []
        for count in range(number):
            self.scores.append(0)

    def getName(self):
        """Returns the student's name."""
        return self.name
  
    def setScore(self, i, score):
        """Resets the ith score, counting from 1."""
        self.scores[i - 1] = score

    def getScore(self, i):
        """Returns the ith score, counting from 1."""
        return self.scores[i - 1]
   
    def getAverage(self):
        """Returns the average score."""
        return sum(self.scores) / len(self.scores)
    
    def getHighScore(self):
        """Returns the highest score."""
        return max(self.scores)

    def __eq__(self, other):
        """Compares if two students' names are equal."""
        if isinstance(other, Student):
            return self.name == other.name
        return False

    def __lt__(self, other):
        """Compares if the current student's name is lexicographically less than the other student's name."""
        if isinstance(other, Student):
            return self.name < other.name
        return False

    def __ge__(self, other):
        """Compares if the current student's name is lexicographically greater than or equal to the other student's name."""
        if isinstance(other, Student):
            return self.name >= other.name
        return False

    def __str__(self):
        """Returns the string representation of the student."""
        return "Name: " + self.name + "\nScores: " + \
               " ".join(map(str, self.scores))

def main():
    """A simple test."""
    student1 = Student("Ken", 5)
    student2 = Student("Alice", 5)


    for i in range(1, 6):
        student1.setScore(i, 90)
        student2.setScore(i, 95)
    

    print(student1)
    print(student2)


    print(f"\nIs {student1.getName()} equal to {student2.getName()}? {student1 == student2}")
    print(f"Is {student1.getName()} less than {student2.getName()}? {student1 < student2}")
    print(f"Is {student1.getName()} greater than or equal to {student2.getName()}? {student1 >= student2}")

if __name__ == "__main__":
    main()
