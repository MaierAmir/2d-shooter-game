import pygame
import random

# screen coords
#   0 | -----------------------------
#     | ` (0,0)
#     |
#     |
#  360|
#     |
#     |
#     |                             . (1280,720)
#  720| -----------------------------
#     0             640           1280


# pygame setup
pygame.init()
x = 1280
y = 720
screen = pygame.display.set_mode((x, y))
clock = pygame.time.Clock()
obstacles = []
enemyList = []
npcbullets = []
bullets = []
consumables = []
player_img = pygame.image.load("player.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (40, 40))
enemy_img = pygame.image.load("enemy.png").convert_alpha()
enemy_img = pygame.transform.scale(enemy_img, (40, 40))
reloadIndicator = False
running = True
dt = 0
menutimer = 1
reload = 0
resetList = 0
runtime = 0
bossActive = False
plyrAni = 0

shot = False
lastShot = 0
bullet = pygame.Vector2(0, 0)
playerhit = False
phTime = 0
player_pos = pygame.Vector2(50, 50)
pausetime = 6
advance = False
lvlscore = 0
score = 0
time = 0
dirSwitchTime = 10  # time after how long the enemy will switch directions
font = pygame.font.SysFont("Arial", 40)
hitMarkerFont = pygame.font.SysFont("Arial", 30)
UIFont = pygame.font.SysFont("Arial", 20)

inv = []

lev4 = False


# for torubleshooting obj rects

objbox = False


def loadimg(file, xp, yp):
    img = pygame.image.load(file).convert_alpha()
    return pygame.transform.scale(img, (xp, yp))

l4enemy = loadimg("l4e.png",40,40)
sq1 = loadimg("invbox.png",200,90)
select = loadimg("sq.png",100,90)
menubg = loadimg("BG.png", 1280, 720)
Window = loadimg("Window.png", x / 3, 500)
scoreUI = loadimg("Score.png", 235, 45)
waypoint = loadimg("wp.png", 30, 50)
blank = loadimg("blank.png", 1, 1)
crash = loadimg("csps.png", 400, 300)
plyrback = loadimg("playerback.png", 40, 40)

bar = loadimg("Table.png", 175, 35)
healthbar = loadimg("Boss_HP_Table.png", 1040, 20)
gh = loadimg("gh3.png", 90, 90)
bossimg = loadimg("boss.png",90,100)
l2obj1 = loadimg("sp1.png", 250, 150)
l2obj2 = loadimg("sp2.png", 300, 200)
l2obj3 = loadimg("sp3.png", 50, 100)
l2obj4 = loadimg("sp4.png", 50, 100)

pwalkR = []
pwalkL = []
pwalkR.append(loadimg("1.png",40,40))
pwalkR.append(loadimg("2.png",40,40))
pwalkR.append(loadimg("3.png",40,40))

pwalkL.append(loadimg("4.png",40,40))
pwalkL.append(loadimg("5.png",40,40))
pwalkL.append(loadimg("6.png",40,40))

pindex =0
plyr = pwalkR[0]

# main menu
mainmenu = True
while mainmenu:

    screen.blit(menubg, (0, 0))
    # rect = pygame.Rect(425, 501, 400, 114)  # for start button
    # pygame.draw.rect(screen, "green", rect)
    screen.blit(loadimg("Header.png", 978, 108), (140, 200))
    screen.blit(loadimg("Start_BTN.png", 410, 121), (420, 500))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if event.button == 1 and 425 < mouse_x < 825 and 501 < mouse_y < 615:  # Left click
                mainmenu = False


class Gun:
    def __init__(self):
        self.id = "pistol"
        self.ammo = 30
        self.magCapacity = 15
        self.mag = self.magCapacity
        self.reloadTime = 2
        self.damage = 20
        self.fireRate = 0.3  # time between each bullet shot
        self.range = 300
        self.img = loadimg("pistol.png", 70, 40)

    def smg(self):
        self.id = "smg"
        self.magCapacity = 30
        self.mag = self.magCapacity
        self.reloadTime = 2.5
        self.damage = 30
        self.fireRate = 0.15
        self.range = 400
        self.img = loadimg("smg.png", 70, 40)

    def ar(self):
        self.id = "ar"
        self.magCapacity = 40
        self.mag = self.magCapacity
        self.reloadTime = 3
        self.damage = 40
        self.fireRate = 0.2
        self.range = 500
        self.img = loadimg("ar.png", 70, 40)

    def sniper(self):
        self.id = "sinper"
        self.magCapacity = 1
        self.mag = self.magCapacity
        self.reloadTime = 4
        self.damage = 200
        self.fireRate = 4
        self.range = 2000
        self.img = loadimg("sniper.png", 70, 40)

    def shotgun(self):
        self.id = "shotgun"
        self.magCapacity = 5
        self.mag = self.magCapacity
        self.reloadTime = 3
        self.damage = 35
        self.fireRate = 0.5
        self.range = 300
        self.img = loadimg("shotgun.png", 70, 40)

    def shipGun(self):
        self.id = "shipGun"
        self.magCapacity = 50
        self.mag = self.magCapacity
        self.reloadTime = 2
        self.damage = 35
        self.fireRate = 0.05
        self.range = 300
        self.img = loadimg("blank.png", 70, 40)

    def pickupGun(self,gunType):
        global inv, gun

        method = getattr(self, f'{gunType}')
        method()


gun = Gun()
# enemygun = Gun()
# enemygun.mag = 9999

def gunpickup(name):
    global inv, gun,player
    gun2 = Gun()
    gun2.pickupGun(name)
    gun = gun2
    player.gun = gun2
    if not any(getattr(g, "id", None) == name for g in inv):
        inv.append(gun2)


class Obstacle:
    def __init__(self, w, l, xp, yp, graphic):
        self.img = graphic
        self.width = w
        self.length = l
        self.pos = pygame.Vector2(xp, yp)
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.length)

    def draw(self):
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.length)

        if objbox:
            pygame.draw.rect(screen, "green", self.rect)

        screen.blit(self.img, (self.pos.x, self.pos.y))


class Character:

    def __init__(self, typec, xmin, xmax, ymin, ymax):
        self.npclastshot = 0
        self.enemyPos = pygame.Vector2(random.randint(xmin, xmax), random.randint(ymin, ymax))
        self.health = 100
        self.typeChar = typec
        self.killed = False
        self.rect = pygame.Rect(self.enemyPos.x, self.enemyPos.y, 40, 40)
        self.enemyDir = pygame.Vector2(random.randint(0, x), random.randint(0, y)).normalize()
        self.enemyRange = 200
        self.hit = False
        self.hitMarkerTime = 0
        self.hitCount = 0
        self.hitpos = 30
        self.gun = Gun()
        self.playerimg = player_img
        self.enemyimg = enemy_img
        self.w= 40
        self.h= 40

    def draw(self):
        global player
        if self.typeChar:
            self.rect = pygame.Rect(player_pos.x, player_pos.y, 40, 40)
            if objbox:
                pygame.draw.rect(screen, "purple", self.rect)

            screen.blit(self.playerimg, (player_pos.x, player_pos.y))

        else:

            self.rect = pygame.Rect(self.enemyPos.x, self.enemyPos.y, self.w, self.h)
            if objbox:
                pygame.draw.rect(screen, "red", self.rect)

            screen.blit(self.enemyimg, (self.enemyPos.x, self.enemyPos.y))

            if self.hit and self.hitMarkerTime < 2:
                for i in range(self.hitCount):
                    screen.blit(hitMarkerFont.render("-" + str(player.gun.damage), True, "pink"),
                                (self.enemyPos.x + 40, self.enemyPos.y - 40 - i * self.hitpos))
                self.hitMarkerTime += dt

            else:
                self.hit = False
                self.hitMarkerTime = 0
                self.hitCount = 0

            if self.enemyimg == bossimg:
                bossHP = loadimg("bosshp.png", self.health*0.06, 8)
                screen.blit(bossHP, (self.enemyPos.x + 15, self.enemyPos.y - 15))

    def enemymove(self, dir):

        temppx = self.enemyPos.x
        temppy = self.enemyPos.y
        if 1240 > self.enemyPos.x > 0:
            temppx += dir.x * 20 * dt

        if 640 > self.enemyPos.y > 0:
            temppy += dir.y * 20 * dt

        npcblocked = False
        trect = pygame.Rect(temppx, temppy, 40, 40)
        for i in obstacles:
            if trect.colliderect(i.rect):
                npcblocked = True

        if not npcblocked:
            self.enemyPos.x = temppx
            self.enemyPos.y = temppy

        self.draw()

    def enemyUpdate(self):

        global x
        global y

        if time >= dirSwitchTime:
            self.enemyDir = pygame.Vector2(random.randint(-x, x), random.randint(-y, y))
            self.enemyDir = self.enemyDir.normalize()
            self.enemymove(self.enemyDir)

        else:
            self.enemymove(self.enemyDir)

        self.shootplayer()

    def enemyUpdateL4(self):
        global x
        global y

        self.enemyPos.y += 0.8
        self.draw()
        self.shootplayer()

    def shootplayer(self):
        global enemy_img, bossimg, lev4
        if self.enemyPos.distance_to(player_pos) <= self.enemyRange:
            self.npclastshot = shoot((player_pos - self.enemyPos).normalize(), self.enemyPos, self.npclastshot,
                                     self.gun, npcbullets, self)
            self.npclastshot += dt
            if not self.enemyimg == bossimg and not lev4:
                if player_pos.x < self.enemyPos.x :
                    self.enemyimg = loadimg("enemyback.png", 40, 40)
                else:
                    self.enemyimg = loadimg("enemy.png", 40, 40)


class Bullet:
    def __init__(self, initposX, initposY, direction, shooter):
        self.initial = pygame.Vector2(initposX, initposY)
        self.posx = initposX
        self.posy = initposY
        self.pos = pygame.Vector2(self.posx, self.posy)
        self.shot = False
        self.target = direction
        self.rect = pygame.Rect(self.posx, self.posy, 5, 5)
        self.shooter =shooter

    def draw(self):

        self.rect = pygame.Rect(self.posx, self.posy, 5, 5)
        if self.shooter.typeChar:
            pygame.draw.rect(screen, "blue", self.rect)
        else:
            pygame.draw.rect(screen, "red", self.rect)

    def update(self):
        self.pos = pygame.Vector2(self.posx, self.posy)
        if self.pos.distance_to(self.initial) > self.shooter.gun.range:
            self.shot = False
        self.posx += self.target.x * 600 * dt
        self.posy += self.target.y * 600 * dt
        self.draw()


player = Character(True, 0, 0, 0, 0)


def reloadgun(key):
    global reload, reloadIndicator, bullets

    if gun.mag == 0 and gun.ammo > 0:
        reloadIndicator = True

    if key[pygame.K_r] and gun.mag < gun.magCapacity or reloadIndicator:
        if gun.ammo>0:
            reloadIndicator = True
            if reload >= gun.reloadTime:
                if gun.ammo > gun.magCapacity:
                    gun.ammo -= gun.magCapacity - gun.mag
                    if gun.ammo<0:
                        gun.ammo=0
                    gun.mag = gun.magCapacity
                else:

                    gun.mag += gun.ammo
                    gun.ammo=0
                    if gun.mag > gun.magCapacity:
                        gun.ammo = gun.mag - gun.magCapacity
                        gun.mag -= gun.mag - gun.magCapacity
                    if gun.ammo<0:
                        gun.ammo=0

                reload = 0
                reloadIndicator = False
            else:
                reload += dt
                if reload >= 0.9 * gun.reloadTime:
                    bullets = []
        else:
            reloadIndicator = False


def shoot(targetdir, shooterPos, lastshot, gun, bullet, shooter):
    global reload

    if lastshot >= gun.fireRate and gun.mag > 0:

        if not gun.id == "shotgun":
            temp1 = Bullet(shooterPos.x + 20, shooterPos.y+20, targetdir, shooter)
            temp1.shot = True
            bullet.append(temp1)
        else:
            dir = [pygame.Vector2(targetdir.x - 0.1, targetdir.y - 0.1), targetdir,
                   pygame.Vector2(targetdir.x + 0.1, targetdir.y + 0.1)]  # 0.1 = shotgun pellet spread

            for i in dir:
                temp1 = Bullet(shooterPos.x, shooterPos.y, i, shooter)
                temp1.shot = True
                bullet.append(temp1)


        gun.mag -= 1
        lastshot = 0

    return lastshot


def shootUpdate(chartype, bullet):
    global hit, playerhit, phTime, player

    if not chartype:
        for round in bullet:  # update bullet
            for obstacle in obstacles:
                if round.rect.colliderect(obstacle.rect):
                    round.shot = False
            if round.shot:
                round.update()
                if round.rect.colliderect(player.rect):
                    playerhit = True
                    phTime = 0
                    player.health -= round.shooter.gun.damage
                    if player.health < 0:
                        player.health = 0
                    round.shot = False
                if round.posx >= x:
                    round.shot = False


    else:
        for round in bullet:
            # update bullet
            if round.shot:
                round.update()

                for obstacle in obstacles:
                    if round.rect.colliderect(obstacle.rect):
                        round.shot = False

                for enemy in enemyList:

                    if round.rect.colliderect(enemy.rect):
                        enemy.health -= player.gun.damage
                        if enemy.health < 0:
                            enemy.health = 0
                        round.shot = False
                        enemy.hit = True
                        enemy.hitCount += 1
                        enemy.hitMarkerTime = 0

                    if round.posx >= x:
                        round.shot = False


def menu(menuType, level):
    global menubg, Window, scoreUI, lvlscore, inv, font

    win = loadimg("win.png", 359, 49)
    lose = loadimg("lose.png", 359, 49)
    bar = loadimg("Table.png", 175, 35)

    if not menuType == 5:
        screen.blit(menubg, (0, 0))


    screen.blit(Window, (405, 137))

    if not menuType == 5:
        screen.blit(scoreUI, (500, 300))
        screen.blit(font.render(str(lvlscore), True, (255, 255, 255)), (610, 360))

    if menuType == 1:
        screen.blit(loadimg("PauseHeader.png", 235, 45), (500, 150))
        screen.blit(font.render("Press [ESC] to resume", True, (255, 255, 255)), (455, 500))

    elif menuType == 2:
        screen.blit(win, (437, 150))
        screen.blit(font.render("Press [ESC] to Exit", True, (255, 255, 255)), (475, 500))

    elif menuType == 3:
        screen.blit(lose, (437, 150))

    elif menuType == 4:
        screen.blit(font.render("Level " + str(level), True, (255, 255, 255)), (565, 150))

    elif menuType == 5:
        screen.blit(font.render("Inventory", True, (255, 255, 255)), (555, 150))

        for i in inv:
            screen.blit(select, (x / 2.25, (inv.index(i) * 100 + 225)))
            screen.blit(i.img, (x/2.2,(inv.index(i)*100+250)))
            screen.blit(font.render(str(inv.index(i)+1), True, (255, 255, 255)), (x/2.5,(inv.index(i)*100+250)))


smg = Obstacle(50, 40, x / 2, y / 2, loadimg("smg.png", 50, 40))

ar = Obstacle(60, 40, 900, y / 2, loadimg("ar.png", 60, 40))

shotgun = Obstacle(60, 40, x/2, y / 2, loadimg("shotgun.png", 60, 40))

ammoImg = loadimg("ammo.png", 40, 40)


def intMenu(intkey, menuType):
    global pausetime, running, gun, inv,player
    keys = pygame.key.get_pressed()

    pausetime += 1
    if keys[intkey] and pausetime > 30:

        pause = True
        while pause:
            menu(menuType, 0)
            pygame.display.flip()
            for event1 in pygame.event.get():
                if event1.type == pygame.QUIT:
                    running = False
                if event1.type == pygame.KEYDOWN:
                    if event1.key == intkey:
                        pause = False
                        pausetime = 0
                    if menuType == 5:
                        for i in range(6):
                            if event1.key == getattr(pygame, f'K_{i + 1}') and len(inv) > i:
                                player.gun = inv[i]
                                gun = inv[i]
                                pause = False
                                pausetime = 0
                                break

boss = Character(False,3,3,360,360)
boss.w = 90
boss.h = 100
boss.enemyimg = bossimg
boss.health = 1000
boss.enemyRange = 1000

def pwalking(level):
    global plyrAni, pindex, pwalkR,pwalkL
    if level != 4:
        mousedir = pygame.mouse.get_pos()

        if plyrAni > 0.25:
            pindex += 1

            pindex = pindex % 3
            if mousedir[0] > player_pos.x:
                player.playerimg = pwalkR[pindex]
            else:
                player.playerimg = pwalkL[pindex]
            plyrAni = 0

def gameplay(backg, gamelevel):
    global dt, lastShot, time, reload, reloadIndicator, running, player, runtime, pausetime, lvlscore, player_img, enemygun
    global crash, plyr, bar, healthbar, consumables, playerhit, phTime, score, gun, inv, shotgun, bossActive, boss
    global plyrAni

    bgpointer = 0

    while running and player.health > 0:

        # pygame.QUIT event means the user clicked X to close window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # relevent variables and updating
        alive = 0
        print(boss.killed)
        if gamelevel != 4:
            screen.blit(backg, (0, 0))
        else:
            bgpointer += 2
            if bgpointer >= 720:
                bgpointer = 0
            screen.blit(backg, (0, bgpointer-720))
            screen.blit(backg, (0, bgpointer))



        player.draw()
        # relevent objects per level

        if gamelevel == 1:
            screen.blit(crash, (370, 0))

            if player_pos.distance_to(smg.pos) < 55:
                gunpickup("smg")
                smg.pos = pygame.Vector2(-100, -100)



        elif gamelevel == 2:
            ar.draw()
            car1 = Obstacle(250, 150, 840, 160, l2obj1)
            car2 = Obstacle(250, 150, 840, 475, l2obj1)
            bigship = Obstacle(120, 200, 530, 285, l2obj2)
            car1.draw()
            car2.draw()
            bigship.draw()
            if player_pos.distance_to(ar.pos) < 50:
                gunpickup("ar")
                ar.pos = pygame.Vector2(-100, -100)

        elif gamelevel == 3:

            shotgun.draw()
            if player_pos.distance_to(shotgun.pos) < 50:
                gunpickup("shotgun")
                shotgun.pos = pygame.Vector2(-100, -100)
            if bossActive:
                enemyList.append(boss)
                boss.gun.range = 700
                boss.gun.mag = 99999
                bossActive = False




        # Regeneration

        phTime += dt
        if not playerhit and phTime > 3 and player.health < 100:
            player.health += 1
        elif playerhit and phTime > 3:
            playerhit = False

        # print(playerhit,phTime)

        # enemies / obstacles updating


        for i in obstacles:
            i.draw()

        for enemy in enemyList:
            if not enemy.killed:
                alive += 1
            if enemy.health > 0:
                if gamelevel !=4:
                    enemy.enemyUpdate()
                else:
                    enemy.enemyUpdateL4()
                    if enemy.enemyPos.y > 720:
                        enemy.killed = True
                        enemyList.remove(enemy)

            else:
                enemy.killed = True
                lvlscore += 1
                enemyList.remove(enemy)
                enemy.rect = pygame.Rect(0, 0, 0, 0)
                if gamelevel!=4:
                    consumables.append(Obstacle(40, 40, enemy.enemyPos.x, enemy.enemyPos.y, ammoImg))

        shootUpdate(False, npcbullets)
        for item in consumables:
            item.draw()
            if player_pos.distance_to(item.pos) < 50 and item.img == ammoImg:
                gun.ammo += gun.magCapacity
                consumables.remove(item)

        # input and movement

        blocked = False
        tempx = player_pos.x
        tempy = player_pos.y
        plyrAni += dt
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and gamelevel!=4:
            tempy -= 150 * dt
            pwalking(gamelevel)
        if keys[pygame.K_s]and gamelevel!=4:
            tempy += 150 * dt
            pwalking(gamelevel)
        if keys[pygame.K_a]:
            tempx -= 150 * dt
            pwalking(gamelevel)
        if keys[pygame.K_d]:
            tempx += 150 * dt
            pwalking(gamelevel)
        if plyrAni > 0.5 and gamelevel != 4:
            if pygame.mouse.get_pos()[0] > player_pos.x:
                player.playerimg = pwalkR[0]
            else:
                player.playerimg = pwalkL[0]

        intMenu(pygame.K_ESCAPE,1)
        intMenu(pygame.K_i,5)

        # obstacles interaction

        temprect = pygame.Rect(tempx, tempy, 40, 40)  # to deal with obstacles

        for i in range(len(obstacles)):  #
            if temprect.colliderect(obstacles[i].rect):
                blocked = True
                break

        if not blocked:
            player_pos.x = tempx
            player_pos.y = tempy

        # shooting

        if keys[pygame.K_SPACE] and not reloadIndicator:
            mouse_pos = pygame.mouse.get_pos()  # Returns (x, y)
            direction = pygame.Vector2(mouse_pos) - player_pos
            direction = direction.normalize()  # Make it a unit vector
            lastShot = shoot(direction, player_pos, lastShot, gun, bullets,player)


        shootUpdate(True, bullets)

        lastShot += dt
        reloadgun(keys)

        # UI

        ammoCount = UIFont.render("Ammo: " + str(gun.ammo) + "/" + str(gun.mag), True,
                                  (255, 255, 255))  # (text, anti-aliasing, color)
        playerHealth = UIFont.render("Health: " + str(player.health), True, (255, 255, 255))
        health = loadimg("Boss_HP_Bar_2.png", player.health * 9.9, 10)

        screen.blit(bar, (38, 87))
        screen.blit(bar, (38, 125))
        screen.blit(bar, (38, 163))
        screen.blit(healthbar, (100, 675))
        screen.blit(health, (125, 680))
        screen.blit(gh, (1100, 87))
        screen.blit(gun.img, (1111, 112))

        enemies = UIFont.render("Enemies: " + str(alive), True, (255, 255, 255))
        reloading = UIFont.render("RELOADING..", True, "orange")
        if gun.ammo == 0 and gun.mag == 0 and int(runtime) % 2 == 0:
            noammo = UIFont.render("NO AMMO", True, "red")
            screen.blit(bar, (540, 640))
            screen.blit(noammo, (590, 644))

        screen.blit(ammoCount, (72, 128))
        screen.blit(playerHealth, (85, 90))
        screen.blit(enemies, (85, 166))

        if gun.mag <= 0 or reloadIndicator :
            if gun.ammo >0 and gun.mag < gun.magCapacity:
                screen.blit(bar, (540, 640))
                screen.blit(reloading, (578, 644))



        # advance to next level

        if alive == 0:
            if gamelevel == 1:
                levelAdvance(315, 210, 300, 330, 150, 260)

            elif gamelevel == 2:
                levelAdvance(575, 100, 500, 650, 150, 180)

            elif gamelevel==3 and alive == 0 and not boss.killed:
                bossActive = True

            elif gamelevel ==3 and boss.killed:
                levelAdvance(575, 200, 500, 650, 200, 255)

            elif gamelevel == 4:
                l4spawner()


        print(player_pos)
        pygame.display.flip()  # update frame

        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        dt = clock.tick(60) / 1000
        if time >= dirSwitchTime:
            time = 0
        else:
            time += dt
        runtime += dt



def levelAdvance(wpx, wpy, xmin, xmax, ymin, ymax):
    global waypoint, running, runtime

    wp = Obstacle(1, 1, wpx, wpy, waypoint)
    if int(runtime) % 2 == 0:  # flash wp marker
        wp.draw()

    if xmin < player_pos.x < xmax and ymin < player_pos.y < ymax:
        running = False


def spawnObj(img, h, w, xmin, xmax, ymin, ymax, typeObj, objList):
    global obstacles
    cond = True

    while cond:
        collide = False
        if typeObj:
            obj = Obstacle(h, w, random.randint(xmin, xmax), random.randint(ymin, ymax), img)
        else:
            obj = Character(False, xmin, xmax, ymin, ymax)
        for i in obstacles:
            if obj.rect.colliderect(i.rect):
                collide = True
        if not collide:
            cond = False
            objList.append(obj)
            return obj


    return None


def level1():
    global running, score, lvlscore, gun, smg, inv
    cactusimg = loadimg("cactus2.png", 40, 80)
    rockimg = loadimg("rock2.png", 40, 40)

    bg = loadimg("lvl1bg.png", x, y)

    obstacles.append(Obstacle(270, 170, 460, 70, blank))  # crashed ship
    obstacles.append(Obstacle(40, 60, 415, 210, blank))
    obstacles.append(Obstacle(150, 40, 460, 241, blank))
    obstacles.append(Obstacle(40, 50, 605, 17, blank))  # fin
    obstacles.append(Obstacle(40, 40, 732, 160, blank))
    obstacles.append(Obstacle(30, 40, 428, 164, blank))

    obstacles.append(Obstacle(40, 40, 382, 318, blank))

    for i in range(20):
        if i <= 10:
            spawnObj(rockimg, 40, 40, 75, x, 300, y, True, obstacles)
        else:
            spawnObj(cactusimg, 20, 80, 75, x, 300, y, True, obstacles)

    enemyNum = random.randint(2, 10)
    enemyNum = 1

    inv.append(gun)


    # gun.sniper()
    # enemygun.sniper()
    # enemygun.mag=9999

    for i in range(enemyNum):
        spawnObj(0, 0, 0, 300, 1000, 310, 550, False, enemyList)
    #obj = Character(False, 300, 1000, 310, 550)
    running = True
    gameplay(bg, 1)
    print(lvlscore)
    score += lvlscore


def level2():
    global obstacles, enemyList, bullets, npcbullets, player_pos, menutimer, running, consumables, gun


    #gun.shotgun()

    menutime = 0

    while menutime < 500:
        pygame.display.flip()
        menu(4, 2)
        menutime += menutimer

    player.health = 100
    gun.mag = gun.magCapacity

    player_pos = pygame.Vector2(30, 390)

    obstacles = []
    enemyList = []
    bullets = []
    npcbullets = []
    consumables = []

    stair1 = loadimg("blank.png", 120, 40)
    stair2 = loadimg("blank.png", 20, 20)

    obstacles.append(Obstacle(120, 30, 0, 320, stair1))
    obstacles.append(Obstacle(120, 20, 0, 460, stair1))
    obstacles.append(Obstacle(30, 20, 0, 360, stair2))
    obstacles.append(Obstacle(2, 80, 0, 360, stair2))

    wallh = loadimg("blank.png", 1280, 1)
    obstacles.append(Obstacle(1280, 1, 0, 150, wallh))  # horz walls
    obstacles.append(Obstacle(1280, 1, 0, 630, wallh))
    obstacles.append(Obstacle(1, 478, 1180, 151, wallh))  # vert walls
    obstacles.append(Obstacle(1, 478, 1, 151, wallh))

    obstacles.append(Obstacle(30, 30, 1128, 164, wallh))  # corner wall pieces
    obstacles.append(Obstacle(30, 30, 1150, 600, wallh))
    obstacles.append(Obstacle(40, 40, 6.6, 152, wallh))
    obstacles.append(Obstacle(40, 30, 4.2, 587, wallh))

    obstacles.append(Obstacle(250, 70, 840, 200, blank))  # 2 big cars
    obstacles.append(Obstacle(110, 30, 980, 155, blank))
    obstacles.append(Obstacle(110, 30, 980, 272, blank))

    obstacles.append(Obstacle(250, 70, 840, 520, blank))
    obstacles.append(Obstacle(110, 30, 980, 475, blank))
    obstacles.append(Obstacle(110, 30, 980, 592, blank))

    # obstacles.append(bigship)  # big centre ship
    obstacles.append(Obstacle(75, 170, 555, 300, blank))
    obstacles.append(Obstacle(24, 100, 530, 340, blank))
    obstacles.append(Obstacle(24, 150, 631, 310, blank))

    # small cars
    z = 140
    z1 = 140
    for i in range(10):
        if i < 5:
            obstacles.append(Obstacle(50, 100, z, 165, l2obj3))
            z += 60
        else:
            obstacles.append(Obstacle(50, 100, z1, 525, l2obj4))
            z1 += 60

    enemyNum = random.randint(2, 7)
    enemyNum = 1

    for i in range(enemyNum):
        spawnObj(0, 0, 0, 300, 1000, 310, 550, False, enemyList)

    bg = loadimg("lvl2bg2.png", x, y)
    running = True
    gameplay(bg, 2)


def level3():
    global obstacles, enemyList, bullets, npcbullets, player_pos, menutimer, running, consumables

    menutime = 0

    while menutime < 500:
        pygame.display.flip()
        menu(4, 3)
        menutime += menutimer

    player.health = 1000
    gun.mag = gun.magCapacity

    player_pos = pygame.Vector2(620, 503)
    bg = loadimg("l32.png", x, y)

    obstacles = []
    enemyList = []
    bullets = []
    npcbullets = []
    consumables = []

    obstacles.append(Obstacle(1280, 205, 0, 557, blank))
    obstacles.append(Obstacle(1280, 200, 0, 0, blank))
    obstacles.append(Obstacle(50, 350, 1240, 202, blank))
    obstacles.append(Obstacle(1, 350, 0, 202, blank))

    enemyNum = 1
    for i in range(enemyNum):
        spawnObj(0, 0, 0, 0, 1190, 200, 275, False, enemyList)


    running = True
    gameplay(bg, 3)

def l4spawner():
    for i in range(random.randint(3, 9)):
        opp = spawnObj(0, 0, 0, 200, 1180, 0, 0, False, enemyList)
        opp.enemyimg = l4enemy
        opp.enemyRange = 300
        opp.gun.shipGun()

def level4():
    global obstacles, enemyList, bullets, npcbullets, player_pos, menutimer, running, consumables, player,lev4
    global inv
    lev4=True
    menutime = 0

    while menutime < 500:
        pygame.display.flip()
        menu(4, 4)
        menutime += menutimer

    player.health = 9999
    inv= []

    gunpickup("shipGun")
    player.gun.ammo = 9999

    player_pos = pygame.Vector2(620, 503)
    bg = loadimg("l4bg2.png", x, y)

    obstacles = []
    enemyList = []
    bullets = []
    npcbullets = []
    consumables = []

    player.playerimg = loadimg("pship.png", 40, 40)

    l4spawner()


    running = True
    gameplay(bg,4)



# obstacles.append(smg)
# level1()
# obstacles.append(ar)
#
# if player.health > 0:
#     level2()
# score += lvlscore
#
# if player.health > 0:
#     level3()
# score += lvlscore

if player.health > 0:
    level4()
score += lvlscore
lev4=False

if player.health > 0:
    menu(2, 0)
else:
    menu(3, 0)



pygame.display.flip()

# Game over screen
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        break

pygame.quit()
