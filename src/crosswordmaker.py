from random import shuffle
from enum import Enum
import six
from json import dumps

class Direction(Enum):
    Horizontal = (0,1)
    Vertical = (1,0)

class CrossWordMaker:
    
    """A utility to generate a crossword puzzle."""
    
    def __init__(self, template, dictionary):
        
        """
        Initialises the CrossWordMaker.
        
        Args
            template: list(list(int or bool))
                The grid representing the template for the puzzle, as a
                list of lists containing values identifying whether or not
                each cell is writable or not.
            vocabulary: list(str,)
                The collection of words where to source the puzzle from.               
        """
        
        
        self.template = template
        self.dictionary = dictionary
        self.vocabulary = list(dictionary)
        self.size = (len(self.template[0]), len(self.template))
        self.width, self.height = self.size
        self.board = [['' for _ in range(self.width)] for _ in range(self.height)]
        self.clues = {}
        
    def getWords(self, pattern):
        
        """
        Yields the words in the vocabulary which match
        the given pattern.
        
        Args
            pattern: list(str,)
                The ordered list of individual characters specifying
                a pattern, in which the empty string means any character.
                
        Yields
            word: str
                A word from the vocabulary complying with the pattern.
        """
        
        for word in self.vocabulary:
            if len(word) != len(pattern):
                continue
            valid = True
            for c, p in zip(word, pattern):
                if p and p != c:
                    valid = False
                    break
            if valid:
                yield word
                    
                
    def shuffle(self):
        
        """Shuffles the vocabulary."""
        
        shuffle(self.vocabulary)
        
    def isWritable(self, row, column):
        
        """
        Indicates whether or not the specified cell can be written
        based on the template.
        
        Args
            row: int
            column: int
            
        Returns
            isWritable: bool
        """
        
        return row >= 0 and row < self.height and column >= 0 and column < self.width and self.template[row][column]
    
    def isWritten(self, row, column):
        
        """
        Returns whether or not the specified cell already contains a value.
        
        Args
            row: int
            column: int
            
        Returns
            isWritten: bool or str
        """
        
        return False if not self.isWritable(row, column) else self.board[row][column]
        
    def getSegments(self):
        
        """
        Extracts all segments based on the templates; these are the locations,
        directions and lengths of all sequences of cells where a clue will go.
        
        Returns
            segments: list(tuple(row:int, column:int, length:int, direction:Direction))
        """
        
        for direction in [Direction.Horizontal, Direction.Vertical]:
            dRow, dColumn = direction.value
            for row in range(self.height):
                for column in range(self.width):
                    
                    previousRow, previousColumn = row - dRow, column - dColumn
                    if self.isWritable(previousRow, previousColumn):
                        continue
                    
                    nextRow, nextColumn, length = row, column, 0
                    while self.isWritable(nextRow, nextColumn):
                        length += 1
                        nextRow = nextRow + dRow
                        nextColumn = nextColumn + dColumn
                        
                    if length < 2:
                        continue
                        
                    segment = (row, column, length, direction)
                    yield segment
                    
    def extractWordCharacters(self, row, column, direction):
        
        """
        Extracts the characters placed (if any) for the segment
        identified by the given arguments.
        
        Args
            row: int
            column: int
            direction: Direction
            
        Returns
            wordCharacters: list(str,)
        """
        
        dRow, dColumn = direction.value
        assert self.isSegmentStart(row, column, direction)
        chars = []
        nextRow, nextColumn = row, column
        while self.isWritable(nextRow, nextColumn):
            chars.append(self.board[nextRow][nextColumn])
            nextRow += dRow
            nextColumn += dColumn
        return chars
    
    def isSegmentStart(self, row, column, direction):
        
        """
        Identified whether the given location is a valid start of a clue.
        
        Args
            row: int
            column: int
            direction: Direction
            
        Returns
            isSegmentStart: bool
        """
        
        dRow, dColumn = direction.value
        previousRow, previousColumn = row - dRow, column - dColumn
        return not self.isWritable(previousRow, previousColumn)   
        
    def setWord(self, row, column, direction, word):
        
        """
        Attempts to set a word for the specified location and direction;
        in case some of the cells for the segment are already filled in
        and the characters do not match, the word will not be added.
        
        Args
            row: int
            column: int
            direction: Direction
            word: str
            
        Returns
            wordWasSet: bool
        """
        
        dRow, dColumn = direction.value
        assert self.isSegmentStart(row, column, direction)
        length, nextRow, nextColumn = 0, row, column
        while self.isWritable(nextRow, nextColumn):
            v = self.isWritten(nextRow, nextColumn)
            if not v or (v and v == word[length]):
                nextRow += dRow
                nextColumn += dColumn
                length += 1
            else:
                return False
        if length != len(word):
            return False
        nextRow, nextColumn = row, column
        for char in word:
            self.board[nextRow][nextColumn] = char
            nextRow += dRow
            nextColumn += dColumn
        return True
    
    def removeWord(self, row, column, direction):
        
        """
        Removes a previously added word for the specified location and direction,
        but preserves characters which were added in any of the matching cells
        by other clues.
        
        Args
            row: int
            column: int
            direction: Direction
        """
        
        assert self.isSegmentStart(row, column, direction)
        dRow, dColumn = direction.value
        nextRow, nextColumn = row, column
        while self.isWritable(nextRow, nextColumn):
            otherDirection = Direction.Horizontal if direction == Direction.Vertical else Direction.Vertical
            otherDRow, otherDColumn = otherDirection.value
            if not self.isWritten(nextRow + otherDRow, nextColumn + otherDColumn) and not self.isWritten(nextRow - otherDRow, nextColumn - otherDColumn):
                self.board[nextRow][nextColumn] = ''
            nextRow += dRow
            nextColumn += dColumn

    async def run(self):
        import asyncio
        loop = asyncio.get_running_loop()
        try:
            future = loop.run_in_executor(None, self._run)
            await asyncio.wait_for(future, 15, loop=loop)
            return True
        except asyncio.TimeoutError:
            return False

        self._run()

    def _run(self):
        
        """Runs the creation of the puzzle."""
        
        segments = list(self.getSegments())
        
        segmentsAdded = [] # Tracks all added clues;
        reverts = [0 for s in segments] # Tracks the number of times running was reverted for a clue, used to backtrack;
        i = 0 # Tracks the segment for which a suitbale clue is being searched;
        
        while i < len(segments):
            
            # For every segment, start by shuffling the vocabulary,
            # extract the segment properties and identify the pattern
            # already in place for it, in case other words were already
            # added for some of the cells;
            
            self.shuffle()
            segment = segments[i]
            row, column, length, direction = segment
            pattern = self.extractWordCharacters(row, column, direction)
            
            for word in self.getWords(pattern):
                
                # For every word matching the pattern (if any), do attempt
                # to add it to the board and if successful, add the segment
                # to the list of additions and move to the next segment;
                
                wordWasAdded = self.setWord(row,column,direction,word)
                if wordWasAdded:
                    segmentsAdded.append((segment, word))
                    i += 1
                    break
            else:
                
                # If no valid word could be found, determine how many segments
                # to backtrack for; the logic ensures that if there were two
                # backtracks for any given segment, the running should be
                # backtracked for an additional segment; this is meant to
                # guarantee that search does not get stuck; backtracking involves
                # removing the word for the segment for which backtrack is applied
                # and switching back the index of search; vocabulary is also
                # shuffled;
                
                for j, segment in enumerate(reversed(segmentsAdded)):
                    k = len(segmentsAdded) - j - 1
                    (row, column, _, direction), _ = segment
                    self.removeWord(row, column, direction)
                    reverts[k] += 1
                    if reverts[k] < 2: break
                    else: reverts[k] = 0
                segmentsAdded = segmentsAdded[:-j-1]
                i -= j + 1
                self.shuffle()
                
        # Upon completion, store the results as a map of segment to word;
            
        self.clues = {segment: word for segment, word in segmentsAdded}

    def getClues(self):
        response = []
        indices = {}
        for i, (segment, word) in enumerate(six.iteritems(self.clues)):
            row, column, length, direction = segment
            index = indices.get((row, column), len(indices)+1)
            indices[(row,column)] = index
            response.append(
                {
                    'row': row,
                    'column': column,
                    'length': length,
                    'direction': str(direction).split('.')[-1],
                    'word': word,
                    'definitions': sorted(self.dictionary[word]),
                    'index': index
                }
            )
        return response
