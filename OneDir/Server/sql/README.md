nosetests-2.7 --cover-erase --with-coverage --cover-package=sql_manager

----------------------------------------------------------------------
............................


|Name                                                          |Stmts   |Miss | Cover |  Missing
|--------------------------------------------------------------|--------|-----|-------|------
|/home//PycharmProjects/onedir/Server/__init__              |   0    |  0  |  100% | 
|/home//PycharmProjects/onedir/extra/__init__               |   0    | 0   |  100% |  
|/home//PycharmProjects/onedir/extra/testhelper/__init__    |   0    | 0   |  100% |  
|/home//PycharmProjects/onedir/extra/testhelper/helpers     |  57    | 8   |   86% |  31-34, 61-64
|__init__                                                      |   0    | 0   |  100% |  
|sql_manager                                                   | 131    | 6   |   95% |  200-203, 240, 244
|test_sqlmanager                                               |  82    | 4   |   95% |  45-47, 52
|test_tableadder                                               |  46    | 0   |  100% |  
|test_tablemanager                                             | 156    | 2   |   99% |  34-35
|test_tableremover                                             | 27     | 1   |   96% |  31
|--------------------------------------------------------------|--------|-----|-------|---------
|TOTAL                                                         | 499    |21   | 96%   |


----------------------------------------------------------------------
Ran 28 tests in 0.715s

OK

Note (to pipe):
nosetests-2.7 --cover-erase --with-coverage --cover-package=sql_manager >> README.md 2>&1
