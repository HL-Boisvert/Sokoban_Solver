def solver(node, wallsPositions, mapSize, cansPositionsSolution):
    deadlockList = deadlockList(wallsPositions,mapSize)
    children = findSuccessor(node,wallsPositions,deadlockList)
    return children


def deadlockList(wallsPositions,mapSize):   #Generate Static deadlocks (considering only walls) for the map
    deadlock_list = []
    for i in range(mapSize[0]):  #Map x-size
        for j in range(mapSize[1]):  #Map y-size
                if wallsPositions[i][j] == 0:       #If [i,j] is empty, check if it's a deadlock:
                    if (wallsPositions[i][j + 1] == 1 and wallsPositions[i + 1][j] == 1):
                        deadlock_list.append([i,j])
                    elif (wallsPositions[i + 1][j] == 1 and wallsPositions[i][j - 1] == 1):
                        deadlock_list.append([i,j])
                    elif (wallsPositions[i][j - 1] == 1 and wallsPositions[i - 1][j] == 1):
                        deadlock_list.append([i,j])
                    elif (wallsPositions[i - 1][j] == 1 and wallsPositions[i][j + 1] == 1):
                        deadlock_list.append([i,j])
    return deadlock_list


def findSuccessor(node,wallsPositions,deadlockList):
    listOfChildren = []
    cansCanBePushed(node,wallsPositions)
    accessibleByRobot(listOfChildren,wallsPositions)
    IsDeadlock(listOfChildren,deadlockList)
    return listOfChildren


def isDeadlock(listOfChildren,deadlockList,positionsCansSolution):      #Check static + dynamic deadlocks
    indexesToDelete = []
    for i in range(len(listOfChildren)):
        for j in range(len(listOfChildren[i].getPositionsCans())):
            try:
                if positionsCansSolution.index(listOfChildren[i].getPositionsCans()[j]):   #don't check for deadlock if the stone is on final position
                    pass
            except ValueError:
                for k in range (len(deadlockList)):
                    if deadlockList[k] == listOfChildren[i].getPositionsCans()[j]:     #Check static deadlock
                        indexesToDelete.append(i)

                try:
                    if (listOfChildren[i].getPositionsCans().index([listOfChildren[i].getPositionsCans()[j][0], listOfChildren[i].getPositionsCans()[j][1] + 1]) \
                    and listOfChildren[i].getPositionsCans().index([listOfChildren[i].getPositionsCans()[j][0] + 1, listOfChildren[i].getPositionsCans()[j][1]])):
                        indexesToDelete.append(i)
                except ValueError:
                    pass

                try:
                    if (listOfChildren[i].getPositionsCans().index([listOfChildren[i].getPositionsCans()[j][0] + 1, listOfChildren[i].getPositionsCans()[j][1]]) \
                    and listOfChildren[i].getPositionsCans().index([listOfChildren[i].getPositionsCans()[j][0], listOfChildren[i].getPositionsCans()[j][1] - 1])):
                        indexesToDelete.append(i)
                except ValueError:
                    pass

                try:
                    if (listOfChildren[i].getPositionsCans().index([listOfChildren[i].getPositionsCans()[j][0], listOfChildren[i].getPositionsCans()[j][1] - 1]) \
                    and listOfChildren[i].getPositionsCans().index([listOfChildren[i].getPositionsCans()[j][0] - 1, listOfChildren[i].getPositionsCans()[j][1]])):
                        indexesToDelete.append(i)
                except ValueError:
                    pass

                try:
                    if (listOfChildren[i].getPositionsCans().index([listOfChildren[i].getPositionsCans()[j][0] - 1, listOfChildren[i].getPositionsCans()[j][1]]) \
                    and listOfChildren[i].getPositionsCans().index([listOfChildren[i].getPositionsCans()[j][0], listOfChildren[i].getPositionsCans()[j][1] + 1])):
                        indexesToDelete.append(i)
                except ValueError:
                    pass

    indexesToDelete = sorted(set(indexesToDelete), key=indexesToDelete.index)   #remove identical indexes to not delete other indexes involuntarily
    for index in sorted(indexesToDelete, reverse=True):   #Delete the indexes from biggest to smallest to not delete indexes involuntarily
        del listOfChildren[index]


def accessibleByRobot(listOfChildren,wallsPositions):
    indexesToDelete = []
    for i in range(len(listOfChildren)):
        xRobot = 2 * listOfChildren[i].getPushList()[len(listOfChildren[i].getPushList()) - 1][0][0] \
        - listOfChildren[i].getPushList()[len(listOfChildren[i].getPushList()) - 1][1][0]

        yRobot = 2 * listOfChildren[i].getPushList()[len(listOfChildren[i].getPushList()) - 1][0][1] \
        - listOfChildren[i].getPushList()[len(listOfChildren[i].getPushList()) - 1][1][1]

        for j in range(len(wallsPositions)):
            if (wallsPositions[j][0] == xRobot and wallsPositions[j][1] == yRobot):
                indexesToDelete.append(i)

        for j in range(len(listOfChildren[i].getPositionsCans())):
            if (listOfChildren[i].getPositionsCans()[j][0] == xRobot and listOfChildren[i].getPositionsCans()[j][1] == yRobot):
                indexesToDelete.append(i)

    for index in sorted(indexesToDelete, reverse=True):     #Delete the indexes from biggest to smallest to not delete indexes involuntarily
        del listOfChildren[index]


def cansCanBePushed(node,wallsPositions):
    destination = [0, 0]
    for i in range(len(node.cansPositions)):
        destination[0] = node.cansPositions[i][0] + 1   #0 -> x and 1 -> y
        destination[1] = node.cansPositions[i][1]
        try:
            if node.cansPositions.index(destination):
                pass
        except ValueError:
            if wallsPositions[position[0]][position[1]] == 0:
                positionRobot = cansPositions[i]
                cansPositions[i] = destination
                listOfChildren.append(TreeNode(positionRobot,cansPositions,node.getPushList().append([[positionRobot],[cansPositions[i]]])))

        destination[0] = node.cansPositions[i][0]
        destination[1] = node.cansPositions[i][1] + 1
        try:
            if node.cansPositions.index(destination):
                pass
        except ValueError:
            if wallsPositions[position[0]][position[1]] == 0:
                cansPositions[i] = destination
                listOfChildren.append(TreeNode(positionRobot,cansPositions,node.getPushList().append([[positionRobot],[cansPositions[i]]])))

        destination[0] = node.cansPositions[i][0]
        destination[1] = node.cansPositions[i][1] - 1
        try:
            if node.cansPositions.index(destination):
                pass
        except ValueError:
            if wallsPositions[position[0]][position[1]] == 0:
                cansPositions[i] = destination
                listOfChildren.append(TreeNode(positionRobot,cansPositions,node.getPushList().append([[positionRobot],[cansPositions[i]]])))

        destination[0] = node.cansPositions[i][0] - 1
        destination[1] = node.cansPositions[i][1]
        try:
            if node.cansPositions.index(destination):
                pass
        except ValueError:
            if wallsPositions[position[0]][position[1]] == 0:
                cansPositions[i] = destination
                listOfChildren.append(TreeNode(positionRobot,cansPositions,node.getPushList().append([[positionRobot],[cansPositions[i]]])))


class TreeNode:

    def __init__(self, positionRobot, positionsCans, pushList):
        self.positionRobot = positionRobot
        self.positionsCans = positionsCans
        self.pushList = pushList
        self.parent = None
        self.leftSibling = None
        self.rightSibling = None
        self.firstChild = None

    def getPositionRobot(self):
        return self.positionRobot

    def setPositionRobot(self, data):
        self.positionRobot = positionRobot

    def getParent(self):
        return self.parent

    def setParent(self, parent):
        self.parent = parent

    def getLeftSibling(self):
        return self.leftSibling

    def setLeftSibling(self, leftSibling):
        self.leftSibling = leftSibling

    def getRightSibling(self):
        return self.rightSibling

    def setRightSibling(self, rightSibling):
        self.rightSibling = rightSibling

    def getFirstChild(self):
        return self.firstChild

    def setFirstChild(self, firstChild):
        self.firstChild = firstChild
