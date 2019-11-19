import pygame
import threading
import sys
import math
import time as timee
import sys
import os
from pathlib import Path

PI = 3.1415926535

def LoadConf(ConfName):
    file = open(ConfName, 'r')
    N = 9
    colors = []
    for i in range(N):
        inp = file.readline().split()
        colors.append([int(x) for x in (inp[-3:-1] + [inp[-1]])])
    Is2D = bool(file.readline().split()[-1])
    colors.append(Is2D)
    return colors

CamPos = [0, 0, 0]
CamRot = [0, 0, 0]
SDist = 400
INF = 10 ** 9
SPD = 3000
Mult = 500
RSPD = 1
DefDetStep = 5
SHIFT = 25
DetStep = math.radians(DefDetStep)
MouseSensDiv = 100
ScalingSPD = 10
G0Color, G1Color, G2Color, G3Color, FrameColor, SelectionColor, SelectionTextColor, BGColor, StepSelectionColor, SurfaceMod = LoadConf('GKIT.conf')
#PPos = [0, 0, 0]

def ToCoordSpace(vect, space):
    vct = list(vect)
    for i in range(len(vect)):
        vct[i] = vct[i] + space[i]
    return vct

def MultVect(vect, n):
    Answer = []
    for i in range(len(vect)):
        Answer.append(vect[i] * n)
    return Answer

def Dist(v1, v2):
    return math.sqrt((v1[0] - v2[0]) * (v1[0] - v2[0]) + (v1[1] - v2[1]) * (v1[1] - v2[1]))

def Dist3(v1, v2):
    return math.sqrt((v1[0] - v2[0]) * (v1[0] - v2[0]) + (v1[1] - v2[1]) * (v1[1] - v2[1]) + (v1[2] - v2[2]) * (v1[2] - v2[2]))

def ToNormal(angle):
    return angle % math.radians(360)

def DeltaAngleRadCW(A1, A2):
    A1 = ToNormal(A1)
    A2 = ToNormal(A2)
    if A1 != A2:
        if A1 > A2:
            return A1 - A2
        else:
            return A1 + math.radians(360) - A2
    else:
        return math.radians(360)

def DeltaAngleRadCCW(A2, A1):
    A1 = ToNormal(A1)
    A2 = ToNormal(A2)
    if A1 != A2:
        if A1 > A2:
            return A1 - A2
        else:
            return A1 + math.radians(360) - A2
    else:
        return math.radians(360)

def ToSeconds(minutes):
    return str(int(minutes)) + ' minutes ' + str(int((minutes - int(minutes)) * 6000) / 100) + ' seconds'

def read(FileNames):
    global DetStep
    lines = []
    colors = []
    thimbs = []
    periods = []
    BCounts = []
    GoOnTimes = []
    ProcessTimes = []
    Coms = []
    LGoOnTimes = []
    LProcessTimes = []
    BlockCount = 0
    GlobalText = []
    time = 0
    GLine = -1
    TimeS = 0.01
    tm = timee.monotonic()
    warnings = 0
    errors = 0
    log = open('LOG.txt', 'w')
    if hasattr(sys, '_MEIPASS'):
        #print('Record')
        font = os.path.join('arial.otf')
        font = pygame.font.Font(font, 12)
        IsEXE = True
    else:
        font = pygame.font.Font(None, 24)
    GlobalLength = 0
    for FileName in FileNames:
        try:
            fl = open(FileName, 'r')
            GlobalLength += len(fl.read().split('\n'))
        except:
            scr = pygame.display.set_mode([450, 150])
            scr.fill((100, 0, 0))
            scr.blit(font.render('No file ', 0, (255, 255, 255)), [10, 24])
            scr.blit(font.render(FileName, 0, (255, 255, 255)), [10, 42])
            scr.blit(font.render('Close this window to enter file names again', 0, (255, 255, 255)), [10, 60])
            pygame.display.update()
            KG = True
            while KG:
                for event in pygame.event.get():
                    if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or event.type == pygame.QUIT:
                        KG = False
            pygame.display.quit()
            return 'NoFile'
    print('Your filelength ' + str(GlobalLength) + ' lines. Turn ON simple mode [y/n]')
    if input() == 'y':
        DetStep = math.radians(90)
        print('Turned ON simple mode')
    else:
        DetStep = math.radians(DefDetStep)
    scr = pygame.display.set_mode([450, 150])
    for period, FileName in enumerate(FileNames):
        print('Next file', FileName, '-' * 100, file = log)
        curr_path = Path('.')
        file = open(FileName, 'r')
        x, y, z = (0, 0, 20)
        tx, ty, tz = (0, 0, 20)
        inp = file.readline()
        GLine += 1
        line = 0
        LenMemor = len(lines)
        CSpace = [0, 0, 0]
        LastComand = ''
        LastSpeed = 50
        while (not (inp == 'M30' or inp == 'M30\n')) and (GLine - 3 < GlobalLength):
            TimeMon = timee.monotonic()
            DeltaTime = TimeMon - tm
            tm = TimeMon
            TimeS += DeltaTime
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            percent = max(GLine / GlobalLength, 0)
            PercentSpeed = max(percent / TimeS, 0.01)
            scr.fill((0, 0, 255))
            pygame.draw.rect(scr, (255, 255, 255), [10, 50, 430, 50])
            pygame.draw.rect(scr, (50, 50, 50), [12, 52, 426, 46])
            pygame.draw.rect(scr, (0, 255, 0), [14, 54, 422 * percent, 42])
            scr.blit(font.render(str(int(percent * 100)) + '%', 0, (255, 255, 255)), [10, 10])
            #print((1 - percent) / PercentSpeed)
            scr.blit(font.render('Time - ' + str((1 - percent) / PercentSpeed) + ' s      Time left ' + str(int(TimeS)) + ' s', 0, (255, 255, 255)), [10, 24])
            scr.blit(font.render('Loading file ' + FileName, 0, (255, 255, 255)), [10, 112])
            scr.blit(font.render(inp[:-1], 0, (255, 255, 255)), [10, 130])
            pygame.display.update()
            GlobalText.append(inp)
            #print(line)
            tx, ty, tz = x, y, z
            line += 1
            GLine += 1
            inp = inp.replace(' ', '')
            for i, simb in enumerate(inp):
                if (simb not in '1234567890') and simb != 'G':
                    inp = inp[:i] + ' ' + inp[i:]
                    break
            Comands = inp.split()
            if len(Comands) != 0:
                try:
                    if Comands[0][0] in 'XYZ':
                        IsIncorrect = True
                        print('\nWARNING! ' + '-' * 50, file = log)
                        print('Comand arguments without comand - ' + inp, file = log)
                        print('It may be comand ' + LastComand + '\n', file = log)
                        warnings += 1
                        Comands.append(LastComand)
                        Comands = Comands[::-1]
                    else:
                        IsIncorrect = False
                    if Comands[0] == 'G0' or Comands[0] == 'G00' or (IsIncorrect and (LastComand == 'G0')):
                        LastComand = 'G0'
                        SecondStr = ''
                        Key = ''
                        for simbol in list(Comands[-1]):
                            if simbol == 'X':
                                if Key != '':
                                    if Key == 'X':
                                        print('\nWARNING! Line -', line, '\n    X coordinate was set twice...\n', file = log)
                                        warnings += 1
                                        tx = float(SecondStr)
                                    if Key == 'Y':
                                        ty = float(SecondStr)
                                    if Key == 'Z':
                                        tz = float(SecondStr)
                                    SecondStr = ''
                                Key = 'X'
                            elif simbol == 'Y':
                                if Key != '':
                                    if Key == 'Y':
                                        print('\nWARNING! Line -', line, '\n    Y coordinate was set twice...\n', file = log)
                                        warnings += 1
                                        ty = float(SecondStr)
                                    if Key == 'X':
                                        tx = float(SecondStr)
                                    if Key == 'Z':
                                        tz = float(SecondStr)
                                    SecondStr = ''
                                Key = 'Y'
                            elif simbol == 'Z':
                                if Key != '':
                                    if Key == 'Z':
                                        print('\nWARNING! Line -', line, '\n    Z coordinate was set twice...\n', file = log)
                                        warnings += 1
                                        tz = float(SecondStr)
                                    if Key == 'Y':
                                        ty = float(SecondStr)
                                    if Key == 'X':
                                        tx = float(SecondStr)
                                    SecondStr = ''
                                Key = 'Z'
                            else:
                                SecondStr = SecondStr + simbol
                        if Key == 'X':
                            tx = float(SecondStr)
                        if Key == 'Y':
                            ty = float(SecondStr)
                        if Key == 'Z':
                            tz = float(SecondStr)
                        FSpeed = 4100
                        lines.append([[x * Mult, y * Mult, z * Mult], ToCoordSpace([tx * Mult, ty * Mult, tz * Mult], CSpace)])
                        colors.append(G0Color)
                        thimbs.append(1)
                        periods.append(period)
                        BCounts.append(BlockCount)
                        Coms.append(GLine)
                        GoOnTimes.append(time)
                        LGoOnTimes.append(time)
                        time += Dist3([x, y, z], [tx, ty, tz]) / FSpeed
                        ProcessTimes.append(Dist3([x, y, z], [tx, ty, tz]) / FSpeed)
                        LProcessTimes.append(Dist3([x, y, z], [tx, ty, tz]) / FSpeed)
                        BlockCount += 1
                    elif Comands[0] == 'G1' or Comands[0] == 'G01' or (IsIncorrect and (LastComand == 'G1')):
                        LastComand = 'G1'
                        SecondStr = ''
                        Key = ''
                        for simbol in list(Comands[-1]):
                            if simbol == 'X':
                                if Key != '':
                                    if Key == 'X':
                                        print('\nWARNING! Line -', line, '\n    X coordinate was set twice...\n', file = log)
                                        warnings += 1
                                        tx = float(SecondStr)
                                    if Key == 'Y':
                                        ty = float(SecondStr)
                                    if Key == 'Z':
                                        tz = float(SecondStr)
                                    SecondStr = ''
                                Key = 'X'
                            elif simbol == 'Y':
                                if Key != '':
                                    if Key == 'Y':
                                        print('\nWARNING! Line -', line, '\n    Y coordinate was set twice...\n', file = log)
                                        warnings += 1
                                        ty = float(SecondStr)
                                    if Key == 'X':
                                        tx = float(SecondStr)
                                    if Key == 'Z':
                                        tz = float(SecondStr)
                                    SecondStr = ''
                                Key = 'Y'
                            elif simbol == 'Z':
                                if Key != '':
                                    if Key == 'Z':
                                        print('\nWARNING! Line -', line, '\n    X coordinate was set twice...\n', file = log)
                                        warnings += 1
                                        tz = float(SecondStr)
                                    if Key == 'Y':
                                        ty = float(SecondStr)
                                    if Key == 'X':
                                        tx = float(SecondStr)
                                    SecondStr = ''
                                Key = 'Z'
                            elif simbol == 'F':
                                if Key == 'X':
                                    tx = float(SecondStr)
                                if Key == 'Y':
                                    ty = float(SecondStr)
                                if Key == 'Z':
                                    tz = float(SecondStr)
                                SecondStr = ''
                                Key = 'F'
                            else:
                                SecondStr = SecondStr + simbol
                        if Key == 'X':
                            tx = float(SecondStr)
                        if Key == 'Y':
                            ty = float(SecondStr)
                        if Key == 'Z':
                            tz = float(SecondStr)
                        if Key == 'F':
                            FSpeed = float(SecondStr)
                        SecondStr = ''
                        lines.append([[x * Mult, y * Mult, z * Mult], ToCoordSpace([tx * Mult, ty * Mult, tz * Mult], CSpace)])
                        colors.append(G1Color)
                        thimbs.append(2)
                        periods.append(period)
                        BCounts.append(BlockCount)
                        Coms.append(GLine)
                        GoOnTimes.append(time)
                        LGoOnTimes.append(time)
                        time += Dist3([x, y, z], [tx, ty, tz]) / FSpeed
                        ProcessTimes.append(Dist3([x, y, z], [tx, ty, tz]) / FSpeed)
                        LProcessTimes.append(Dist3([x, y, z], [tx, ty, tz]) / FSpeed)
                        BlockCount += 1
                    elif Comands[0] == 'G2' or Comands[0] == 'G02' or (IsIncorrect and (LastComand == 'G2')) or Comands[0] == 'G3' or Comands[0] == 'G03' or (IsIncorrect and (LastComand == 'G3')):
                        G2 = False
                        if (Comands[0] == 'G2' or Comands[0] == 'G02' or (IsIncorrect and (LastComand == 'G2'))):
                            LastComand = 'G2'
                            G2 = True
                        else:
                            LastComand = 'G3'
                            G2 = False
                        SecondStr = ''
                        Key = ''
                        Cx = x
                        Cy = y
                        RadMet = False
                        for index, simbol in enumerate(list(Comands[-1])):
                            if simbol == 'X':
                                if Key != '':
                                    if Key == 'X':
                                        print('\nWARNING! Line -', line, '\n    X coordinate was set twice...\n', file = log)
                                        warnings += 1
                                        tx = float(SecondStr)
                                    if Key == 'Y':
                                        ty = float(SecondStr)
                                    if Key == 'Z':
                                        tz = float(SecondStr)
                                    SecondStr = ''
                                Key = 'X'
                            elif simbol == 'Y':
                                if Key != '':
                                    if Key == 'Y':
                                        print('\nWARNING! Line -', line, '\n    Y coordinate was set twice...\n', file = log)
                                        warnings += 1
                                        ty = float(SecondStr)
                                    if Key == 'X':
                                        tx = float(SecondStr)
                                    if Key == 'Z':
                                        tz = float(SecondStr)
                                    SecondStr = ''
                                Key = 'Y'
                            elif simbol == 'Z':
                                if Key != '':
                                    if Key == 'Y':
                                        ty = float(SecondStr)
                                    if Key == 'X':
                                        tx = float(SecondStr)
                                    if Key == 'Z':
                                        print('\nWARNING! Line -', line, '\n    Z coordinate was set twice...\n', file = log)
                                        warnings += 1
                                        tz = float(SecondStr)
                                    SecondStr = ''
                                Key = 'Z'
                            elif simbol == 'I':
                                if Key != '':
                                    if Key == 'Y':
                                        ty = float(SecondStr)
                                    if Key == 'X':
                                        tx = float(SecondStr)
                                    if Key == 'Z':
                                        tz = float(SecondStr)
                                    SecondStr = ''
                                Key = 'I'
                            elif simbol == 'J':
                                Cx = x + float(SecondStr)
                                SecondStr = ''
                            elif simbol == 'R':
                                if Key != '':
                                    if Key == 'Y':
                                        ty = float(SecondStr)
                                    if Key == 'X':
                                        tx = float(SecondStr)
                                    if Key == 'Z':
                                        tz = float(SecondStr)
                                RadMet = True
                                SecondStr = ''
                            elif simbol == 'F':
                                FSpeed = float(Comands[1][index + 1:])
                                break
                            else:
                                SecondStr = SecondStr + simbol
                        tx, ty, tz = ToCoordSpace([tx, ty, tz], CSpace)
                        if not RadMet:
                            Cy = y + float(SecondStr)
                            SecondStr = ''
                        else:
                            Radius = float(SecondStr)
                            StVector = [tx - x, ty - y]
                            CP = [x + StVector[0] / 2, y + StVector[1] / 2]
                            PerpVector = [-StVector[1], StVector[0]]
                            TimedVar = Dist((0, 0), StVector) / 2
                            Cxt, Cyt = MultVect(PerpVector, (math.sqrt(Radius * Radius - TimedVar * TimedVar)) / Dist((0, 0), PerpVector))
                            Cxt += CP[0]
                            Cyt += CP[1]
                            Cx = Cxt
                            Cy = Cyt
                            Angle1 = ToAngle(x - Cx, y - Cy)
                            Angle2 = ToAngle(tx - Cx, ty - Cy)
                            Step = (DeltaAngleRadCW(Angle1, Angle2))
                            if (Step > math.radians(180) and Radius > 0) or (Step < math.radians(180) and Radius < 0):
                                Cxt, Cyt = MultVect(MultVect(PerpVector, -1), (math.sqrt(Radius * Radius - TimedVar * TimedVar)) / Dist((0, 0), PerpVector))
                                Cxt += CP[0]
                                Cyt += CP[1]
                            Cx = Cxt
                            Cy = Cyt
                            SecondStr = ''
                            R1 = abs(Radius)
                            R2 = abs(Radius)
                            StepR = 0
                        Angle1 = ToAngle(x - Cx, y - Cy)
                        Angle2 = ToAngle(tx - Cx, ty - Cy)
                        if G2:
                            DetDep = max(int(DeltaAngleRadCW(Angle1, Angle2) / DetStep), 0.01)
                            Step = (DeltaAngleRadCW(Angle1, Angle2)) / DetDep
                        else:
                            DetDep = max(int(DeltaAngleRadCCW(Angle1, Angle2) / DetStep), 0.01)
                            Step = (DeltaAngleRadCCW(Angle1, Angle2)) / DetDep
                        R1 = Dist((x, y), (Cx, Cy))
                        R2 = Dist((tx, ty), (Cx, Cy))
                        StepR = (R2 - R1) / DetDep
                        Pos = [x, y, z]
                        DeltaTimeSum = 0
                        ZStep = (tz - z) / DetDep
                        for i in range(int(DetDep)):
                            if G2:
                                Angle = -Step * i + Angle1
                            else:
                                Angle = Step * i + Angle1
                            Radius = StepR * i + R1
                            NextPos = [math.cos(Angle) * Radius + Cx, math.sin(Angle) * Radius + Cy, z + ZStep * i]
                            lines.append([MultVect(Pos, Mult), MultVect(NextPos, Mult)])
                            if G2:
                                colors.append(G2Color)
                            else:
                                colors.append(G3Color)
                            thimbs.append(2)
                            periods.append(period)
                            BCounts.append(BlockCount)
                            Coms.append(GLine)
                            GoOnTimes.append(time)
                            LGoOnTimes.append(time)
                            time += Dist3(Pos, NextPos) / FSpeed
                            LProcessTimes.append(Dist3(Pos, NextPos) / FSpeed)
                            DeltaTimeSum += Dist3(Pos, NextPos) / FSpeed
                            Pos = NextPos
                        lines.append([MultVect(Pos, Mult), MultVect([tx, ty, tz], Mult)])
                        colors.append(G2Color)
                        thimbs.append(2)
                        periods.append(period)
                        BCounts.append(BlockCount)
                        Coms.append(GLine)
                        GoOnTimes.append(time)
                        LGoOnTimes.append(time)
                        time += Dist3(Pos, [tx, ty, tz]) / FSpeed
                        DeltaTimeSum += Dist3(Pos, [tx, ty, tz]) / FSpeed
                        LProcessTimes.append(Dist3(Pos, [tx, ty, tz]) / FSpeed)
                        for i in range(int(DetDep) + 1):
                            ProcessTimes.append(DeltaTimeSum)
                        BlockCount += 1
                    if Comands[0] == 'G10':
                        SecondStr = ''
                        Key = ''
                        for simbol in list(Comands[-1]):
                            if simbol == 'X':
                                if Key != '':
                                    if Key == 'X':
                                        print('\nWARNING! Line -', line, '\n    X coordinate was set twice...\n', file = log)
                                        warnings += 1
                                        tx = float(SecondStr)
                                    if Key == 'Y':
                                        ty = float(SecondStr)
                                    if Key == 'Z':
                                        tz = float(SecondStr)
                                    SecondStr = ''
                                Key = 'X'
                            elif simbol == 'Y':
                                if Key != '':
                                    if Key == 'Y':
                                        print('\nWARNING! Line -', line, '\n    Y coordinate was set twice...\n', file = log)
                                        warnings += 1
                                        ty = float(SecondStr)
                                    if Key == 'X':
                                        tx = float(SecondStr)
                                    if Key == 'Z':
                                        tz = float(SecondStr)
                                    SecondStr = ''
                                Key = 'Y'
                            elif simbol == 'Z':
                                if Key != '':
                                    if Key == 'Z':
                                        print('\nWARNING! Line -', line, '\n    Z coordinate was set twice...\n', file = log)
                                        warnings += 1
                                        tz = float(SecondStr)
                                    if Key == 'Y':
                                        ty = float(SecondStr)
                                    if Key == 'X':
                                        tx = float(SecondStr)
                                    SecondStr = ''
                                Key = 'Z'
                            else:
                                SecondStr = SecondStr + simbol
                        if Key == 'X':
                            tx = float(SecondStr)
                        if Key == 'Y':
                            ty = float(SecondStr)
                        if Key == 'Z':
                            tz = float(SecondStr)
                        CSpace = [tx, ty, tx]
                except ValueError:
                    print('\nWARNING! ' + '-' * 50, file = log)
                    print('Incorrect comand - ' + inp + '\n', file = log)
                    print(end = '')
            x, y, z = ToCoordSpace([tx, ty, tz], CSpace)
            inp = file.readline()
        if not (GLine - 3 < GlobalLength):
            print('\nWARNING! ' + '-' * 50, file = log)
            print('No end comand M30 readed', file = log)
            print('It is not critical, but be carefull...' + '\n', file = log)
        GlobalText.append(inp)
    pygame.display.quit()
    return (lines, colors, thimbs, periods, BCounts, Coms, GlobalText, GoOnTimes, ProcessTimes, LGoOnTimes, LProcessTimes, BlockCount, time)

def Summ(v1, v2):
    return [v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2]]

def ToAngle(x, y):
    return math.atan2(y, x)

def Rotate(x, y, deg):
    ln = math.sqrt(x * x + y * y)
    A = math.atan2(y, x)
    X = math.sin(A + deg) * ln
    Y = math.cos(A + deg) * ln
    return [X, Y]

def RotateAll(CPost, CRot, lines):
    Answer = []
    CPos = [0, 0, 0]
    multer = MultVect(CPos, -1)
    for line in lines:
        default = [Summ(line[0], CPos), Summ(line[1], CPos)]
        for point in default:
            point[0], point[1] = Rotate(point[1], point[0], CRot[2])
            point[2], point[0] = Rotate(point[0], point[2], CRot[1])
        default = [Summ(default[0], multer), Summ(default[1], multer)]
        Answer.append(default)
    return Answer

def ToLocal(CPosT, CRot, lines):
    Answer = []
    CPos = list(CPosT)
    CPos[0], CPos[1] = Rotate(CPos[1], CPos[0], CRot[2])
    CPos[2], CPos[0] = Rotate(CPos[0], CPos[2], CRot[1])
    for line in lines:
        default = [Summ(CPos, line[0]), Summ(CPos, line[1])]
        Answer.append(default)
    return Answer

def ScreenCoords(lines, ScrDist):
    global INF
    Answer = []
    IsKalcked = False
    for i in range(len(lines)):
        line = lines[i]
        if not((line[0][0] < ScrDist and line[1][0] < ScrDist) or (2 * Dist3(line[0], line[1]) / (Dist3(line[0], [0, 0, 0]) + Dist3(line[1], [0, 0, 0])) < 0.001)):
            if line[0][0] > ScrDist and line[1][0] > ScrDist:
                if not(IsKalcked):
                    if line[0][0] != 0:
                        KY1 = line[0][1] / line[0][0]
                        KZ1 = line[0][2] / line[0][0]
                    else:
                        KY1 = line[0][1] / 0.01
                        KZ1 = line[0][2] / 0.01
                else:
                    KY1 = KY2
                    KZ1 = KZ2
                if line[1][0] != 0:
                    KY2 = line[1][1] / line[1][0]
                    KZ2 = line[1][2] / line[1][0]
                else:
                    KY2 = line[1][1] / 0.01
                    KZ2 = line[1][2] / 0.01
                Answer.append([[KY1 * ScrDist, KZ1 * ScrDist], [KY2 * ScrDist, KZ2 * ScrDist], i])
                IsKalcked = True
            else:
                if line[0][0] < ScrDist:
                    Point = line[1]
                else:
                    Point = line[0]
                if Point[0] != 0:
                    KY1 = Point[1] / Point[0]
                    KZ1 = Point[2] / Point[0]
                else:
                    KY1 = Point[1] / 0.01
                    KZ1 = Point[2] / 0.01
                kY = (line[0][1] - line[1][1]) / (line[0][0] - line[1][0] if line[0][0] - line[1][0] != 0 else 0.01)
                bY = line[1][1] - line[1][0] * kY
                YY = kY * ScrDist + bY
                kZ = (line[0][2] - line[1][2]) / (line[0][0] - line[1][0] if line[0][0] - line[1][0] != 0 else 0.01)
                bZ = line[1][2] - line[1][0] * kZ
                ZZ = kZ * ScrDist + bZ
                Answer.append([[KY1 * ScrDist, KZ1 * ScrDist], [YY, ZZ], i])
                IsKalcked = False
        else:
            IsKalcked = False
    return Answer

def Centrix(coord, SCRX, SCRY):
    return [-coord[0] + SCRX / 2, -coord[1] + SCRY / 2]

def RotateSpeed(spd, rot):
    Answer = list(spd)
    Answer[1] = -spd[0] * math.cos(rot) + spd[1] * math.sin(rot)
    Answer[0] = -spd[1] * math.cos(rot) + -spd[0] * math.sin(rot)
    return Answer

def RotateLine2D(spd, rot):
    Answer = list(spd)
    Answer[1] = -spd[0] * math.cos(rot) + spd[1] * math.sin(rot)
    Answer[0] = -spd[1] * math.cos(rot) + -spd[0] * math.sin(rot)
    return Answer

def GetPhresePosition(time, lines, STimes, PTimes):
    Index = 0
    for i in range(len(STimes)):
        if STimes[i] <= time < STimes[i] + PTimes[i]:
            Index = i
    Shift = MultVect([lines[Index][1][0] - lines[Index][0][0], lines[Index][1][1] - lines[Index][0][1], lines[Index][1][2] - lines[Index][0][2]], (time - STimes[Index]) / PTimes[Index])
    Pos = [lines[Index][0][0] + Shift[0], lines[Index][0][1] + Shift[1], lines[Index][0][2] + Shift[2]]
    return Pos

def PhreseMesh(pos):
    x, y, z = pos
    return [[[x, y, z], [x + 300, y + 300, z + 2000]], [[x, y, z], [x + 300, y - 300, z + 2000]], [[x, y, z], [x - 300, y - 300, z + 2000]], [[x, y, z], [x - 300, y + 300, z + 2000]], [[x + 300, y + 300, z + 2000], [x + 300, y - 300, z + 2000]], [[x + 300, y - 300, z + 2000], [x - 300, y - 300, z + 2000]], [[x - 300, y - 300, z + 2000], [x - 300, y + 300, z + 2000]], [[x - 300, y + 300, z + 2000], [x + 300, y + 300, z + 2000]]]

def GetDraftTransform(lines, ScreenS, shift):
    global INF
    SX = ScreenS[0] - 2 * shift
    SY = ScreenS[1] - 2 * shift
    MinX = INF
    MaxX = -INF
    MinY = INF
    MaxY = -INF
    for line in lines:
        for point in line:
            X, Y = point[:2][::-1]
            if X > MaxX:
                MaxX = X
            if X < MinX:
                MinX = X
            if Y > MaxY:
                MaxY = Y
            if Y < MinY:
                MinY = Y
    if (MaxX - MinX) / SX > (MaxY - MinY) / SY:
        mult = SX / (MaxX - MinX)
    else:
        mult = SY / (MaxY - MinY)
    Start = [-MinX * mult + shift, -MinY * mult + shift]
    StartPosition = [-(MaxY + MinY) // 2, -(MaxX + MinX) // 2, 0]
    return [[mult, Start], StartPosition]

def SetToSurf(lines, colors, surf, transform):
    mult, Start = transform
    for i, line in enumerate(lines):
        pygame.draw.line(surf, colors[i], [Start[0] + line[0][1] * mult, Start[1] + line[0][0] * mult], [Start[0] + line[1][1] * mult, Start[1] + line[1][0] * mult])
    return surf

def main():
    global SPD, RSPD, MouseSensDiv, DetStep, CamPos, CamRot, SurfaceMod, SDist
    pygame.init()
    KeepGoing = True
    print('\n' * 3 + '-' * 70)
    print('G-code KIT, G-code viewer by Kudryashov Ilya')
    print('Default settings:')
    print('Movement speed -', SPD)
    print('Keyboard rotation speed -', RSPD)
    print('Mouse sensitive -', 1 / MouseSensDiv)
    print('Curve detalisation step angle -', DetStep)
    print('\n' * 5)
    while True:
        KeepGoing = True
        print('Enter names of files to open with format (.gcode, .txt and other) splited by [Space]')
        FileNamesInp = input()
        result = read(FileNamesInp.split())
        if result != 'NoFile':
            lines, colors, thimbs, periods, BCs, Coms, ProgText, GoOnTimes, PTimes, LGoOnTimes, LPTimes, N, Time = result
        else:
            KeepGoing = False
        if KeepGoing:
            linesT = list(lines)
            pygame.init()
            MaxLen = 0
            for string in ProgText:
                if len(string) > MaxLen:
                    MaxLen = len(string)
            #print(LGoOnTimes)
            #print(LPTimes)
            SCRX = 1000
            SCRY = 700
            SurfView = pygame.Surface([SCRX, SCRY])
            LastFrame = pygame.Surface([SCRX, SCRY])
            SurfViewTransf, CamPos = GetDraftTransform(lines, [SCRX, SCRY], SHIFT)
            SVMult = SurfViewTransf[0]
            SVPos = SurfViewTransf[1]
            SetToSurf(lines, colors, SurfView, SurfViewTransf)
            try:
                screen = pygame.display.set_mode([SCRX, SCRY])
            except:
                print('Screen ERROR --------------------------------------------------------------')
            Speed = [0, 0, 0]
            RSpeed = [0, 0, 0]
            ShowI = 0
            clock = pygame.time.Clock()
            tm = timee.monotonic()
            #font = pygame.font.render('arial', 24)
            SwipeR = False
            ColorMode = False
            AnimationS = 0
            AnimTimer = 0
            Inform = False
            font = None
            if hasattr(sys, '_MEIPASS'):
                #print('Record')
                font = os.path.join('arial.otf')
                font = pygame.font.Font(font, 12)
                IsEXE = True
            else:
                font = pygame.font.Font(None, 24)
                IsEXE = False
            Controlls = True
            PAnimS = 0
            PAnimT = 0
            ShowPhrese = False
            K = 1
            RDelta = [0, 0, 0]
            linesT = RotateAll(CamPos, CamRot, lines)
            Change = True
        while KeepGoing:
            #print('abc')
            Screenshot = False
            TimeMonot = timee.monotonic()
            DeltaTime = TimeMonot - tm
            tm = TimeMonot
            screen.fill(BGColor)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    KeepGoing = False
                    pygame.display.quit()
                    print('Exit from program or load new file? [load / exit]')
                    if input() == 'exit':
                        pygame.quit()
                        exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        Speed[0] -= 1
                    if event.key == pygame.K_s:
                        Speed[0] += 1
                    if event.key == pygame.K_a:
                        Speed[1] += 1
                    if event.key == pygame.K_d:
                        Speed[1] -= 1
                    if event.key == pygame.K_LCTRL:
                        Speed[2] += 1
                    if event.key == pygame.K_SPACE:
                        Speed[2] -= 1
                    if event.key == pygame.K_UP:
                        RSpeed[1] -= RSPD
                    if event.key == pygame.K_DOWN:
                        RSpeed[1] += RSPD
                    if event.key == pygame.K_LEFT:
                        RSpeed[2] += RSPD
                    if event.key == pygame.K_RIGHT:
                        RSpeed[2] -= RSPD
                    if event.key == pygame.K_q:
                        AnimationS -= 1
                    if event.key == pygame.K_e:
                        AnimationS += 1
                    if event.key == 61:
                        SPD += 500
                    if event.key == 45:
                        SPD -= 500
                    if event.key == pygame.K_2:
                        PAnimS += 1
                        ShowPhrese = True
                    if event.key == pygame.K_1:
                        PAnimS -= 1
                        ShowPhrese = True
                    if event.key == pygame.K_LSHIFT:
                        ColorMode = not ColorMode
                        Change = True
                    if event.key == pygame.K_ESCAPE:
                        KeepGoing = False
                        pygame.display.quit()
                        print('Exit from program or load new file? [load / exit]')
                        if input() == 'exit':
                            pygame.quit()
                            exit()
                    if event.key == pygame.K_F2:
                        Inform = not Inform
                    if event.key == pygame.K_F1:
                        Controlls = not Controlls
                    if event.key == pygame.K_F12:
                        Screenshot = True
                    if event.key == pygame.K_COMMA:
                        MouseSensDiv += 10
                    if event.key == pygame.K_PERIOD and MouseSensDiv > 10:
                        MouseSensDiv -= 10
                    if event.key == pygame.K_F3:
                        SurfaceMod = not SurfaceMod
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        Speed[0] -= -1
                    if event.key == pygame.K_s:
                        Speed[0] += -1
                    if event.key == pygame.K_a:
                        Speed[1] += -1
                    if event.key == pygame.K_d:
                        Speed[1] -= -1
                    if event.key == pygame.K_LCTRL:
                        Speed[2] += -1
                    if event.key == pygame.K_SPACE:
                        Speed[2] -= -1
                    if event.key == pygame.K_UP:
                        RSpeed[1] -= -RSPD
                    if event.key == pygame.K_DOWN:
                        RSpeed[1] += -RSPD
                    if event.key == pygame.K_LEFT:
                        RSpeed[2] += -RSPD
                    if event.key == pygame.K_RIGHT:
                        RSpeed[2] -= -RSPD
                    if event.key == pygame.K_q:
                        AnimationS += 1
                    if event.key == pygame.K_e:
                        AnimationS -= 1
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        if not SurfaceMod:
                            SDist += ScalingSPD
                            Change = True
                        else:
                            K += ScalingSPD / 400
                    if event.button == 5 and SDist > ScalingSPD * 2:
                        if not SurfaceMod:
                            SDist -= ScalingSPD
                            Change = True
                        elif K > ScalingSPD / 400:
                            K -= ScalingSPD / 400
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    SwipeR = True
                    pygame.mouse.get_rel()
                    pygame.mouse.set_visible(False)
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    SwipeR = False
                    pygame.mouse.set_visible(True)
            if KeepGoing:
                RDelta = Summ(MultVect(RSpeed, DeltaTime), RDelta)
                CamPos = Summ(CamPos, MultVect(RotateSpeed(MultVect(Speed, SPD), -CamRot[2] - PI / 2), DeltaTime))
                CamRot = Summ(CamRot, MultVect(RSpeed, DeltaTime))
                if SwipeR:
                    MRel = pygame.mouse.get_rel()
                    RDelta = Summ(RDelta, [0, MRel[1] / MouseSensDiv, -MRel[0] / MouseSensDiv])
                    CamRot = Summ(CamRot, [0, MRel[1] / MouseSensDiv, -MRel[0] / MouseSensDiv])
                if RDelta != [0, 0, 0] and (not SurfaceMod):
                    linesT = RotateAll(CamPos, CamRot, lines)
                    RDelta = [0, 0, 0]
                    Change = True
                if Speed != [0, 0, 0]:
                    Change = True
                AnimTimer += DeltaTime * AnimationS
                ShowI = int(AnimTimer * 10) % N
                period = periods[BCs.index(ShowI)]
                PAnimT = (PAnimT + (PAnimS * DeltaTime) / 60) % Time
                if AnimationS != 0:
                    Change = True
                if not SurfaceMod:
                    if Change:
                        LocalModel = ToLocal(CamPos, CamRot, linesT)
                        ARR = ScreenCoords(LocalModel, SDist)
                        LPos = [0, 0]
                        for ln in ARR:
                            i = ln[2]
                            if not(Dist(ln[0], ln[1]) < 2):
                                LPos = Centrix(ln[1], SCRX, SCRY)
                                if (BCs + [-1])[i] != ShowI:
                                    pygame.draw.line(screen, (colors[i] if period == periods[i] or ColorMode else (50, 50, 50)), Centrix(ln[0], SCRX, SCRY), Centrix(ln[1], SCRX, SCRY), thimbs[i])
                                else:
                                    pygame.draw.line(screen, StepSelectionColor, Centrix(ln[0], SCRX, SCRY), Centrix(ln[1], SCRX, SCRY), 5)
                            elif not(Dist(LPos, ln[0]) < 2):
                                PixPos = [int(x) for x in Centrix(ln[0], SCRX, SCRY)]
                                if (BCs + [-1])[i] != ShowI:
                                    screen.set_at(PixPos, (colors[i] if period == periods[i] or ColorMode else (50, 50, 50)))
                                else:
                                    pygame.draw.line(screen, StepSelectionColor, Centrix(ln[0], SCRX, SCRY), Centrix(ln[1], SCRX, SCRY), 5)
                        LastFrame = screen.copy()
                        Change = False
                    else:
                        screen.blit(LastFrame, (0, 0))
                    if ShowPhrese:
                        PhreseLines = RotateAll(CamPos, CamRot, PhreseMesh(GetPhresePosition(PAnimT, lines, LGoOnTimes, LPTimes)))
                        for ln in ScreenCoords(ToLocal(CamPos, CamRot, PhreseLines), SDist):
                            pygame.draw.line(screen, (255, 255, 0), Centrix(ln[0], SCRX, SCRY), Centrix(ln[1], SCRX, SCRY), 2)
                else:
                    SV = pygame.transform.scale(SurfView, [int(SCRX * K), int(SCRY * K)])
                    screen.blit(SV, [int(-K * (SVPos[0] + -CamPos[1] * SVMult) + SCRX // 2), int(-K * (SVPos[1] + -CamPos[0] * SVMult) + SCRY // 2)])
                    pygame.draw.circle(screen, StepSelectionColor, [int(SCRX // 2), int(SCRY // 2)], 5, 5)
                    DirLine = RotateLine2D([0, 20], CamRot[2] + PI / 2)
                    pygame.draw.line(screen, StepSelectionColor, [int(SCRX // 2), int(SCRY // 2)], [int(DirLine[0] + SCRX // 2), int(DirLine[1] + SCRY // 2)])
                if Inform:
                    screen.blit(font.render('Distance to screen surface: ' + str(SDist), 0, (255, 255, 255)), [0, 0])
                    screen.blit(font.render('Movement speed: ' + str(SPD), 0, (255, 255, 255)), [0, 30])
                    screen.blit(font.render('Arrow rotation speed: ' + str(math.degrees(RSPD)) + '                   Mouse senitive: ' + str(1 / MouseSensDiv), 0, (255, 255, 255)), [0, 60])
                    screen.blit(font.render('World camera position: ' + 'X ' + str(-CamPos[0] / Mult) + '   Y ' + str(-CamPos[1] / Mult) + '   Z ' + str(-CamPos[2] / Mult), 0, (255, 255, 255)), [0, 90])
                    screen.blit(font.render('World camera rotation: ' + 'X ' + str(CamRot[0] / Mult) + '   Y ' + str(CamRot[1] / Mult) + '   Z ' + str(CamRot[2] / Mult), 0, (255, 255, 255)), [0, 120])
                    screen.blit(font.render('Global step: ' + str(ShowI + 1), 0, (255, 255, 255)), [0, 150])
                    screen.blit(font.render('Time: ' + ToSeconds(Time), 0, (255, 255, 255)), [0, 180])
                    screen.blit(font.render('Step start time: ' + ToSeconds(GoOnTimes[BCs.index(ShowI)]), 0, (255, 255, 255)), [0, 210])
                    screen.blit(font.render('Step action time: ' + ToSeconds(PTimes[BCs.index(ShowI)]), 0, (255, 255, 255)), [0, 240])
                    screen.blit(font.render('Phrese animation time speed: ' + str(PAnimS), 0, (255, 255, 255)), [0, 270])
                    screen.blit(font.render('Global phrese animation time: ' + ToSeconds(PAnimT), 0, (255, 255, 255)), [0, 300])
                    LN = Coms[BCs.index(ShowI)]
                    SimbMult = 9.5
                    if IsEXE:
                        SimbMult = 7
                    pygame.draw.rect(screen, FrameColor, [0, SCRY - 280, (MaxLen + 4) * SimbMult, 280])
                    pygame.draw.rect(screen, SelectionColor, [0, SCRY - 181, (MaxLen + 4) * SimbMult, 16])
                    for i in range(-4, 5):
                        if 0 <= LN + i < len(ProgText):
                            if i != -1:
                                screen.blit(font.render((ProgText[LN + i][:-1] if ProgText[LN + i][-1] == '\n' else ProgText[LN + i]), 0, (255, 255, 255)), [0, SCRY - (5 - i) * 30])
                            else:
                                screen.blit(font.render('>>' + ProgText[LN + i][:-1] + '<<', 0, SelectionTextColor), [0, SCRY - (5 - i) * 30])
                if Controlls:
                    screen.fill((0, 0, 255))
                    screen.blit(font.render('Moving - WASD, [LCtrl], [Space]                Zoom - [Mouse wheel Up/Down]', 0, (255, 255, 255)), [0, 0])
                    screen.blit(font.render('Rotation - [Arrows] or [Mouse]                 Mous sensitive change - [,], [.]', 0, (255, 255, 255)), [0, 30])
                    screen.blit(font.render('Speed change - [+], [-]                        Phrese animation speed change - [1], [2]', 0, (255, 255, 255)), [0, 60])
                    screen.blit(font.render('Step change - [Q], [E]                         Screenshot - [F12]', 0, (255, 255, 255)), [0, 90])
                    screen.blit(font.render('Show all models in color mode (On/Off) - [LShift]', 0, (255, 255, 255)), [0, 120])
                    screen.blit(font.render('World information - [F2]                       2D draft view ON/OFF - [F3]', 0, (255, 255, 255)), [0, 150])
                    screen.blit(font.render('Help bar Open/Close - [F1]', 0, (255, 255, 255)), [0, 180])
                pygame.display.update()
                if Screenshot:
                    pygame.image.save(screen, FileNamesInp.replace('.', '~').replace(' ', '_') + str(int(timee.time())) + ".png")
                    screen.fill((255, 255, 255))
                    TTM = timee.monotonic()
                    pygame.display.update()
                    while timee.monotonic() - TTM < 0.1:
                        ksjdnfckjdandkfnaskndskn = 0
                clock.tick(60)
    pygame.quit()
main()


def func():
	print('Get some loolz!')

print("The gratest program ever by the best one programmer... What only says [Get some loolz!]")
func()
print("Kolya's code")
