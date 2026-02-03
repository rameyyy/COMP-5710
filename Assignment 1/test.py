import unittest
import source  # type: ignore

FLOATERROR = 'error: not a float or int'
DIVBYZEROERROR = 'error: can not divide by zero'

class TestCalc(unittest.TestCase):
    def testSub1(self):
        self.assertEqual(1, source.performSub(3, 2), "Bug in code, check please!")   

    def testSub2(self):
        self.assertEqual(4, source.performSub(6, 2), "Bug in code, check please!")
        
    def testAdd1(self):
        self.assertEqual(4, source.performAdd(1, 3), "Bug in code, check please!")
        
    def testAdd2(self):
        self.assertEqual(3.5, source.performAdd('1.5', '2.0'), "Bug in code, check please!")

    def testAdd3(self):
        self.assertEqual(FLOATERROR, source.performAdd('1.5', '2.0!'), "Bug in code, check please!")
    
    def testMultiply1(self):
        self.assertEqual(6, source.performMultiply(2, 3), "Bug in code, check please!")
    
    def testMultiply2(self):
        self.assertEqual(6, source.performMultiply('2', 3), "Bug in code, check please!")
    
    def testMultiply3(self):
        self.assertEqual(FLOATERROR, source.performMultiply('ABC', '3.5'), "Bug in code, check please!")
    
    def testDivide1(self):
        self.assertEqual(2, source.performDivide(6, 3), "Bug in code, check please!")
    
    def testDivide2(self):
        self.assertEqual(2, source.performDivide(6, '3'), "Bug in code, check please!")
    
    def testDivide3(self):
        self.assertEqual(DIVBYZEROERROR, source.performDivide(6, 0), "Bug in code, check please!")

    def testDivide4(self):
        self.assertEqual(0, source.performDivide(0, 3), "Bug in code, check please!")
    
    def testDivide5(self):
        self.assertEqual(DIVBYZEROERROR, source.performDivide(3, '0'), "Bug in code, check please!")
    
    def testSquareRoot1(self):
        self.assertEqual(2, source.performSquareRoot(4), 'Bug in code, check please!')

    def testSquareRoot2(self):
        self.assertEqual(2, source.performSquareRoot('4'), 'Bug in code, check please!')
    
    def testSquareRoot3(self):
        self.assertEqual(FLOATERROR, source.performSquareRoot('4A'), 'Bug in code, check please!')
    
    def testSquareRoot4(self):
        self.assertEqual(0, source.performSquareRoot(0), 'Bug in code, check please!')
        
    
   
   
if __name__ == '__main__': 
    unittest.main()
