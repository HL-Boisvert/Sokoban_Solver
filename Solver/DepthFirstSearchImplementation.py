# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
#                          Sokoban Solver
#-------------------------------------------------------------------------------


#To do:
#Use heuristics
#Convert DFS solution to instructions for robot using path-finding

import copy
import pygame

class ListNode(object):
    def __init__(self, val,pushList):
        self.val = val
        self.next = None
        self.pushList = pushList

    def getData(self):
        return self.val

    def setData(self, val):
        self.val = val

    def getPushList(self):
        return self.pushList

    def setPushList(self, pushList):
        self.pushList = pushList

    def getNext(self):
        return self.next

    def setNext(self, next):
        self.next = next

class LinkedList(object):

    def __init__(self, value, pushList):
        self.count = 0
        self.head = ListNode(value,pushList)
        node = self.head

    def insert(self, data, pushList):
        new_node = ListNode(data,pushList)
        new_node.setNext(self.head)
        self.head = new_node
        self.count += 1

    def append(self, value, pushList):
        current = self.head
        if current:
            while current.getNext() != None:
                current = current.getNext()
            current.setNext(ListNode(value,pushList))
        else:
            self.head = ListNode(item)

    def insertAt(self, idx, val, pushList):
        if idx > self.count + 2:
            return

        if idx == 0:
            self.insert(val)
        else:
            tempIdx = 0
            node = self.head
            while tempIdx < idx - 1:
                node = node.getNext()
                tempIdx += 1
            continuation = node.getNext()
            insertion = ListNode(val,pushList)
            node.setNext(insertion)
            node.getNext().setNext(continuation)
            self.count += 1

    def find(self, val):
        item = self.head
        while item != None:
            if item.getData() == val:
                return item
            else:
                item = item.getNext()

        return None

    def deleteAt(self, idx):
        if idx > self.count + 1:
            return
        if idx == 0:
            self.head = self.head.getNext()
        else:
            tempIdx = 0
            node = self.head
            while tempIdx < idx - 1:
                node = node.getNext()
                tempIdx += 1
            node.setNext(node.getNext().getNext())
            self.count -= 1

    def outputList(self):
        tempnode = self.head
        while (tempnode != None):
            print(tempnode.getData())
            tempnode = tempnode.getNext()

class TreeNode:
    '''
      Parameters
      ----------
      positionRobot : int[]
          [x,y]
      positionsCans : int[][]
          [[x1,y1],...]
      pushList
          [[[InitialPositionPush1],[FinalPositionPush1]],...]
      '''
    def __init__(self, positionRobot, positionsCans, pushList, positionsCansList):
        self.positionRobot = positionRobot
        self.positionsCans = positionsCans
        self.positionsCansList = positionsCansList
        self.pushList = pushList
        self.parent = None
        self.leftSibling = None
        self.rightSibling = None
        self.firstChild = None
        self.depth = None

    def getPositionRobot(self):
        return self.positionRobot

    def setPositionRobot(self, positionRobot):
        self.positionRobot = positionRobot

    def getPositionsCans(self):
        return self.positionsCans

    def setPositionsCans(self, positionsCans):
        self.positionsCans = positionsCans

    def getPushList(self):
        return self.pushList

    def setPushList(self, pushList):
        self.pushList = pushList

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

    def getDepth(self):
        return self.depth

    def setDepth(self,depth):
        self.depth = depth

    def getPositionsCansList(self):
        return self.positionsCansList

    def setPositionsCansList(self, positionsCansList):
        self.positionsCansList = positionsCansList


class Tree():
    '''
      Parameters
      ----------
      positionRobot : int[]
          [line,column]
      positionsCans : int[][]
          [[x1,y1],...]
      pushList
          [[[InitialPositionPush1],[FinalPositionPush1]],...]
      '''
    def __init__(self, root,wallsPositions,mapSize,cansPositionsSolution):
        self.wallsPositions = wallsPositions
        self.mapSize = mapSize
        self.deadlockList = self.deadlockList(self.wallsPositions,self.mapSize)
        self.cansPositionsSolution = cansPositionsSolution
        self.root = root
        self.firstBorn = self.solver(self.root,self.wallsPositions,self.mapSize,self.cansPositionsSolution,self.deadlockList)[0]
        self.currentNode = self.firstBorn
        self.currentValue = self.currentNode.getPositionsCans()
        self.start = self.currentValue
        self.visited = LinkedList(self.root.getPositionsCans(),self.root.getPushList()) # list of positionsCans values visited in previous nodes


    def deadlockList(self,wallsPositions,mapSize):   #Generate Static deadlocks (considering only walls) for the map
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

    def isDeadlock(self,listOfChildren,deadlockList,positionsCansSolution):      #Check static + dynamic deadlocks
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

    def accessibleByRobot(self,listOfChildren,wallsPositions):  #Delete children that require the robot to do an illegal move (regarding cans or walls)
        indexesToDelete = []
        for i in range(len(listOfChildren)):
            #Calculate the position the robot should have to push the can that was moved between parent and listOfChildren[i]
            #xRobot = 2 * initialPosition - finalPosition
            xRobot = 2 * listOfChildren[i].getPushList()[len(listOfChildren[i].getPushList()) - 1][0][0][0] \
            - listOfChildren[i].getPushList()[len(listOfChildren[i].getPushList()) - 1][1][0][0]     #[0] needs to be added (weird?)
            #print("xrobot",xRobot)
            yRobot = 2 * listOfChildren[i].getPushList()[len(listOfChildren[i].getPushList()) - 1][0][0][1] \
            - listOfChildren[i].getPushList()[len(listOfChildren[i].getPushList()) - 1][1][0][1]
            #print("yrobot",yRobot)
            #print("pCanne1",listOfChildren[i].getPositionsCans()[0])
            #print("pCanne2",listOfChildren[i].getPositionsCans()[1])

            try:
                if wallsPositions[xRobot][yRobot] == 1:     #Check for walls
                    indexesToDelete.append(i)
            except IndexError:
                indexesToDelete.append(i)

            for j in range(len(listOfChildren[i].getPositionsCans())):  #Check for other Cans
                if (listOfChildren[i].getPositionsCans()[j][0] == xRobot and listOfChildren[i].getPositionsCans()[j][1] == yRobot):
                    flag = 0
                    for k in range(len(indexesToDelete)):   #Avoid adding j to indexesToDelete if it is already there from first j loop
                        if indexesToDelete[k] == i:
                            flag = 1
                    if flag == 0:
                        indexesToDelete.append(i)

        indexesToDelete = list(set(indexesToDelete))
        for index in sorted(indexesToDelete, reverse=True):     #Delete the indexes from biggest to smallest to not delete indexes involuntarily
            del listOfChildren[index]

    def canCansBePushed(self,node,wallsPositions,listOfChildren,positionsCansSolution,i):
        destination1 = [0, 0]
        destination2 = [0, 0]
        destination3 = [0, 0]
        destination4 = [0, 0]

        """for k in range (len(positionsCansSolution)):
            if node.getPositionsCans()[i] == positionsCansSolution[k]: #If the can is already at solution
                return"""

        destination1[0] = node.getPositionsCans()[i][0] + 1   #0 -> ligne and 1 -> colonne
        destination1[1] = node.getPositionsCans()[i][1]

        destination2[0] = node.getPositionsCans()[i][0]
        destination2[1] = node.getPositionsCans()[i][1] + 1

        destination3[0] = node.getPositionsCans()[i][0]
        destination3[1] = node.getPositionsCans()[i][1] - 1

        destination4[0] = node.getPositionsCans()[i][0] - 1
        destination4[1] = node.getPositionsCans()[i][1]

        flag = 0 # no cans at the destination and can not on solution
        for j in range (len(node.getPositionsCans())):
            if node.getPositionsCans()[j] == destination1:  #If there's a can at the destination
                flag = 1

        if flag == 0:
            #print("pas de canne a destination1 et canne pas deja sur solution")
            if wallsPositions[destination1[0]][destination1[1]] == 0 and destination1[0] > 0 and destination1[0] < self.mapSize[0] \
            and destination1[1] > 0 and destination1[1] < self.mapSize[1]:
                #print("pas de mur a dest1 et dest1 pas hors limites")
                positionRobot = copy.copy(node.getPositionsCans()[i])
                updatedPositionsCans = copy.copy(node.getPositionsCans())
                updatedPositionsCans[i] = destination1
                newChild = TreeNode(positionRobot,updatedPositionsCans,copy.copy(node.getPushList()),copy.copy(node.getPositionsCansList()))
                newChild.getPushList().append([[positionRobot],[updatedPositionsCans[i]]])
                newChild.getPositionsCansList().append(updatedPositionsCans)
                listOfChildren.append(newChild)
                #print("dest1",listOfChildren[len(listOfChildren)-1].getPositionsCans()[i])


        #print("destination2",destination2[0],destination2[1])
        flag = 0
        for j in range (len(node.getPositionsCans())):
            if node.getPositionsCans()[j] == destination2:  #If there's a can at the destination
                flag = 1

        if flag == 0:
            if wallsPositions[destination2[0]][destination2[1]] == 0 and destination2[0] > 0 and destination2[0] < self.mapSize[0] \
            and destination2[1] > 0 and destination2[1] < self.mapSize[1]:
                #print("pas de mur a dest2 et dest2 pas hors limites")
                positionRobot = copy.copy(node.getPositionsCans()[i])
                updatedPositionsCans = copy.copy(node.getPositionsCans())
                updatedPositionsCans[i] = destination2
                newChild = TreeNode(positionRobot,updatedPositionsCans,copy.copy(node.getPushList()),copy.copy(node.getPositionsCansList()))
                newChild.getPushList().append([[positionRobot],[updatedPositionsCans[i]]])
                newChild.getPositionsCansList().append(updatedPositionsCans)
                listOfChildren.append(newChild)
                #print("dest2",listOfChildren[len(listOfChildren)-1].getPositionsCans()[i])

        flag = 0
        for j in range (len(node.getPositionsCans())):
            if node.getPositionsCans()[j] == destination3:  #If there's a can at the destination
                flag = 1

        if flag == 0:
            if wallsPositions[destination3[0]][destination3[1]] == 0 and destination3[0] > 0 and destination3[0] < self.mapSize[0] \
            and destination3[1] > 0 and destination3[1] < self.mapSize[1]:
                #("pas de mur a dest3 et dest3 pas hors limites")
                positionRobot = copy.copy(node.getPositionsCans()[i])
                updatedPositionsCans = copy.copy(node.getPositionsCans())
                updatedPositionsCans[i] = destination3
                newChild = TreeNode(positionRobot,updatedPositionsCans,copy.copy(node.getPushList()),copy.copy(node.getPositionsCansList()))
                newChild.getPushList().append([[positionRobot],[updatedPositionsCans[i]]])
                newChild.getPositionsCansList().append(updatedPositionsCans)
                listOfChildren.append(newChild)
                #print("dest3",listOfChildren[len(listOfChildren)-1].getPositionsCans()[i])

        flag = 0
        for j in range (len(node.getPositionsCans())):
            if node.getPositionsCans()[j] == destination4:  #If there's a can at the destination
                flag = 1

        if flag == 0:
            if wallsPositions[destination4[0]][destination4[1]] == 0 and destination4[0] > 0 and destination4[0] < self.mapSize[0] \
            and destination4[1] > 0 and destination4[1] < self.mapSize[1]:
                #print("pas de mur a dest4 et dest4 pas hors limites")
                positionRobot = copy.copy(node.getPositionsCans()[i])
                updatedPositionsCans = copy.copy(node.getPositionsCans())
                updatedPositionsCans[i] = destination4
                newChild = TreeNode(positionRobot,updatedPositionsCans,copy.copy(node.getPushList()),copy.copy(node.getPositionsCansList()))
                newChild.getPushList().append([[positionRobot],[updatedPositionsCans[i]]])
                newChild.getPositionsCansList().append(updatedPositionsCans)
                listOfChildren.append(newChild)

    def findSuccessor(self,node,wallsPositions,deadlockList,cansPositionsSolution):
        AlistOfChildren = []
        for i in range (len(node.getPositionsCans())):
            self.canCansBePushed(node,wallsPositions,AlistOfChildren,cansPositionsSolution,i)
        self.accessibleByRobot(AlistOfChildren,wallsPositions)
        self.isDeadlock(AlistOfChildren,deadlockList,cansPositionsSolution)
        return AlistOfChildren

    def solver(self,node,wallsPositions,mapSize,cansPositionsSolution,deadlockList): #To optimize put deadlockList outside of solver()
        children = self.findSuccessor(node,wallsPositions,deadlockList,cansPositionsSolution)
        for i in range (len(children)):
            children[i].setParent(node)
            children[i].setDepth(node.getDepth() + 1)
        for i in range (len(children) - 1):
            children[i].setRightSibling(children[i + 1])
        for i in range (len(children) - 1):
            children[i + 1].setLeftSibling(children[i])
        return children

    def isVisited(self, val):
        if self.visited.find(val):
            return True
        else:
            return False

    def childDepthFirstSearch(self, searchVal,wallsPositions,mapSize,maxDepth):
        #print("firstBorn",self.firstBorn.getPositionsCans(),"pushList",self.firstBorn.getPushList())
        #print("new call DFS")
        if len(searchVal) != len(self.root.getPositionsCans()):
            return("Error: Number of cans is not coherent with solution.")

        c = 0
        while c < 1000000:
            self.searchVal = searchVal
            if sorted(self.currentValue) == sorted(self.searchVal) or self.currentValue == self.root.getPositionsCans():
                condition = 1

                #copy self.path and reset for future method calls
                self.firstBorn = self.solver(self.root,self.wallsPositions,self.mapSize,self.cansPositionsSolution,self.deadlockList)[0]
                self.solutionNode = self.currentNode
                self.currentNode = self.firstBorn
                self.currentValue = self.currentNode.getPositionsCans()
                self.start = self.currentValue
                self.visited = LinkedList(self.root.getPositionsCans(),self.root.getPushList())

                if condition == 1:
                    return(self.solutionNode)
                else:
                    return("Value not found")

            else:

                nonVisitedSiblings = []
                for m in range (len(self.solver(self.currentNode.getParent(),self.wallsPositions,self.mapSize,self.cansPositionsSolution,self.deadlockList))):
                    if self.visited.find(self.solver(self.currentNode.getParent(),self.wallsPositions,self.mapSize,self.cansPositionsSolution,self.deadlockList)[m].getPositionsCans()) == None:
                        nonVisitedSiblings.append(m)

                nonVisitedChildren = []
                for m in range (len(self.solver(self.currentNode,self.wallsPositions,self.mapSize,self.cansPositionsSolution,self.deadlockList))):
                    if self.visited.find(self.solver(self.currentNode,self.wallsPositions,self.mapSize,self.cansPositionsSolution,self.deadlockList)[m].getPositionsCans()) == None:
                        nonVisitedChildren.append(m)
                    #print("child ", m, self.solver(self.currentNode,self.wallsPositions,self.mapSize,self.cansPositionsSolution,self.deadlockList)[m].getPositionsCans())

                # Moves in the tree
                if len(self.solver(self.currentNode,self.wallsPositions,self.mapSize,self.cansPositionsSolution,self.deadlockList)) != 0 \
                and self.isVisited(self.solver(self.currentNode,self.wallsPositions,self.mapSize,self.cansPositionsSolution,self.deadlockList)[0].getPositionsCans()) == False \
                and self.currentNode.getDepth() <= maxDepth:
                    # parent --> firstChild (not yet visited)
                    self.currentNode = self.solver(self.currentNode,self.wallsPositions,self.mapSize,self.cansPositionsSolution,self.deadlockList)[0]
                    self.currentValue = self.currentNode.getPositionsCans()
                    self.visited.append(self.currentValue,self.currentNode.getPushList())
                    #print("went to firstChild")
                    #print('currentNode positionCans',self.currentNode.getPositionsCans())
                    #print("currentNode Pushlist",self.currentNode.getPushList())

                elif len(nonVisitedChildren) != 0 and self.currentNode.getDepth() <= maxDepth:
                    # parent --> NonFirstChild (not yet visited)
                    self.currentNode = self.solver(self.currentNode,self.wallsPositions,self.mapSize,self.cansPositionsSolution,self.deadlockList)[nonVisitedChildren[0]]
                    self.currentValue = self.currentNode.getPositionsCans()
                    self.visited.append(self.currentValue,self.currentNode.getPushList())
                    #print("went to NonFirstChild")
                    #print('currentNode positionCans',self.currentNode.getPositionsCans())
                    #print("currentNode Pushlist",self.currentNode.getPushList())

                elif self.currentNode.getRightSibling() != None and self.isVisited(self.currentNode.getRightSibling().getPositionsCans()) == False:
                    # sibling --> right_sibling (not yet visited)
                    self.currentNode = self.currentNode.getRightSibling()
                    self.currentValue = self.currentNode.getPositionsCans()
                    self.visited.append(self.currentValue,self.currentNode.getPushList())
                    #print("went to rightSibling not yet visited")
                    #print('currentNode positionCans',self.currentNode.getPositionsCans())
                    #print("currentNode Pushlist",self.currentNode.getPushList())

                elif self.currentNode.getRightSibling() == None and self.currentNode.getLeftSibling():
                    # right_most_sibling --> left_sibling (already visited)
                    self.currentNode = self.currentNode.getLeftSibling()
                    self.currentValue = self.currentNode.getPositionsCans()
                    #print("right_most_sibling --> left_sibling (already visited)")
                    #print('currentNode positionCans',self.currentNode.getPositionsCans())
                    #print("currentNode Pushlist",self.currentNode.getPushList())

                elif self.currentNode.getLeftSibling() != None and self.isVisited(self.currentNode.getRightSibling().getPositionsCans()) == True:
                    # sibling (not left-most or right-most) --> left_sibling (already visited)
                    self.currentNode = self.currentNode.getLeftSibling()
                    self.currentValue = self.currentNode.getPositionsCans()
                    #print("sibling (not left-most or right-most) --> left_sibling (already visited)")
                    #print('currentNode positionCans',self.currentNode.getPositionsCans())
                    #print("currentNode Pushlist",self.currentNode.getPushList())

                elif len(nonVisitedSiblings) != 0:
                    #sibling --> non visited sibling
                    self.currentNode = self.solver(self.currentNode.getParent(),self.wallsPositions,self.mapSize,self.cansPositionsSolution,self.deadlockList)[nonVisitedSiblings[0]]
                    self.currentValue = self.currentNode.getPositionsCans()
                    #print("sibling --> non visited sibling")
                    #print('currentNode positionCans',self.currentNode.getPositionsCans())
                    #print("currentNode Pushlist",self.currentNode.getPushList())

                else:
                    # left_most_sibling --> parent (already visited)
                    #print("go back to parent", self.currentNode.getParent().getPushList())
                    self.currentNode = self.currentNode.getParent()
                    self.currentValue = self.currentNode.getPositionsCans()

                c += 1

        print("Need to increase search cap")



class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

def astar(map, start, end):
    """Returns a list of tuples as a path from the given start to the given end in the given map"""

    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    # Loop until you find the end
    while len(open_list) > 0:

        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1] # Return reversed path

        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (len(map) - 1) or node_position[0] < 0 or node_position[1] > (len(map[len(map)-1]) -1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if map[node_position[0]][node_position[1]] != 0:
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is on the closed list
            for closed_child in closed_list:
                if child == closed_child:
                    continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            # Child is already in the open list
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    continue

            # Add the child to the open list
            open_list.append(child)


class main():
    root = TreeNode([1,10],[[2,8],[2,6]],[],[[2,8],[2,6]])
    root.setDepth(0)
    maxDepth = 1000

    walls = [[1,1,1,1,1,1,1,1,1,1,1,1],
             [1,1,0,0,0,1,0,0,0,0,0,1],
             [1,1,0,0,0,0,0,0,0,0,0,1],
             [1,1,0,0,0,1,1,0,0,0,0,1],
             [1,0,0,0,0,1,0,0,1,1,1,1],
             [1,0,0,0,0,0,0,0,1,1,1,1],
             [1,1,1,1,1,1,1,1,1,1,1,1]]


    positionsCansSolution = [[4,2],[4,3]]
    mapSize = [6,11]
    t = Tree(root,walls,mapSize,positionsCansSolution)

    def buildPath(solutionNode,walls,root,mapSize):
        path = []

        for i in range (0,len(solutionNode.getPushList())-1):
            wallsTemp = walls
            for j in range(len(root.getPositionsCans())):
                for k in range(mapSize[0]+1):
                    for l in range(mapSize[1]+1):
                        if (solutionNode.getPositionsCansList()[i+2][j][0] == k and solutionNode.getPositionsCansList()[i+2][j][1] == l):
                            wallsTemp[k][l] = 1

            p1 = astar(wallsTemp,(solutionNode.getPushList()[i][0][0][0],solutionNode.getPushList()[i][0][0][1]),\
            (solutionNode.getPushList()[i+1][0][0][0],solutionNode.getPushList()[i+1][0][0][1]))
            for k in range (len(p1)):
                path.append(p1[k])
        try:
            for i in range(len(path)):
                if (path[i+1] == path[i]):
                    del path[i]
        except IndexError:
            return path

    path = buildPath(t.childDepthFirstSearch(positionsCansSolution,walls,mapSize,maxDepth),walls,root,mapSize)
    print(path)


main()

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
WINDOW_HEIGHT = 800
WINDOW_WIDTH = 800

def UI():
    global SCREEN, CLOCK
    pygame.init()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pygame.time.Clock()
    SCREEN.fill(BLACK)

    while True:
        drawGrid()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()

def drawGrid():
    blockSize = 80 #Set the size of the grid block
    for x in range(0, WINDOW_WIDTH, blockSize):
        for y in range(0, WINDOW_HEIGHT, blockSize):
            rect = pygame.Rect(x, y, blockSize, blockSize)
            pygame.draw.rect(SCREEN, WHITE, rect, 1)
