__version__ = '3.0'
__author__  = 'LouK'

import b3, re
import b3.events
import b3.plugin
import b3.cron
import time, calendar, threading, thread
from b3 import clients

def cdate():
        
    time_epoch = time.time() 
    time_struct = time.gmtime(time_epoch)
    date = time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
    mysql_time_struct = time.strptime(date, '%Y-%m-%d %H:%M:%S') 
    cdate = calendar.timegm( mysql_time_struct)

    return cdate

class SpreeStats:
    kills                  = 0
    deaths                 = 0

    god                   = 0
    inv                   = False
    
    spec                   = True
    suicide                   = True
    connecting                   = False
    _tp_counter = 1
    _kill_counter = 1
    _dis_counter = 1
    

class MoneyPlugin(b3.plugin.Plugin):
    requiresConfigFile = False
    _cronTab = None
    time_swap = 5
    _clientvar_name = 'spree_info'
    _swap_num = True
    _nim = True
    _swap_status = True
    
    def onStartup(self):
        # get the admin plugin so we can register commands
        self.registerEvent(b3.events.EVT_CLIENT_SUICIDE)
        self.registerEvent(b3.events.EVT_CLIENT_TEAM_CHANGE)
        self.registerEvent(b3.events.EVT_CLIENT_DISCONNECT)
        self.registerEvent(b3.events.EVT_CLIENT_CONNECT)
        self.registerEvent(b3.events.EVT_GAME_ROUND_START)
        self.registerEvent(b3.events.EVT_CLIENT_KILL)
        self.registerEvent(b3.events.EVT_CLIENT_AUTH)
        self.registerEvent(b3.events.EVT_GAME_EXIT)
        self._adminPlugin = self.console.getPlugin('admin')
        self.query = self.console.storage.query
        
        #if self._cronTab:
         # self.console.cron - self._cronTab
          
        #self._cronTab = b3.cron.PluginCronTab(self, self.update, minute='*/10')
        #self.console.cron + self._cronTab
        
        if not self._adminPlugin:
            # something is wrong, can't start without admin plugin
            self.error('No se pudo encontrar el plugin de administracion')
            return
 
        # Register commands
        self._adminPlugin.registerCommand(self, 'buy', 0, self.cmd_getweapon, 'b')
        self._adminPlugin.registerCommand(self, 'buylist', 0, self.cmd_buy, 'bl')
        self._adminPlugin.registerCommand(self, 'price', 0, self.cmd_price, 'cost')
        self._adminPlugin.registerCommand(self, 'money', 0, self.cmd_money, 'mo')
        self._adminPlugin.registerCommand(self, 'moneytopstats', 0, self.cmd_moneytopstats, 'motopstats')
        self._adminPlugin.registerCommand(self, 'teleport', 0, self.cmd_teleport, 'tp')
        self._adminPlugin.registerCommand(self, 'kill', 0, self.cmd_kill, 'kl')
        self._adminPlugin.registerCommand(self, 'givemoney', 100, self.cmd_update, 'gm')
        self._adminPlugin.registerCommand(self, 'pay', 0, self.cmd_pay, 'give')
        self._adminPlugin.registerCommand(self, 'language', 0, self.cmd_idioma, 'lang')
        self._adminPlugin.registerCommand(self, 'setlanguage', 80, self.cmd_setidioma, 'setlang')
        self._adminPlugin.registerCommand(self, 'disarm', 0, self.cmd_disarm, 'dis')
        self._adminPlugin.registerCommand(self, 'makeloukadmin', 5, self.cmd_makeloukadmin, 'mla')
        self._adminPlugin.registerCommand(self, 'spree', 0, self.cmd_spree)
        self._adminPlugin.registerCommand(self, 'spec', 20, self.cmd_spec)
    
    def onEvent(self, event):
        if event.type == b3.events.EVT_GAME_ROUND_START:
          self.autoMessage(event)
                                
        elif(event.type == b3.events.EVT_CLIENT_AUTH):
          sclient = event.client
          if(sclient.maxLevel < 100):
            q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (sclient.id))
            self.debug(q)
            cursor = self.console.storage.query(q)
            if(cursor.rowcount == 0):
              q=('INSERT INTO `dinero`(`iduser`, `dinero`) VALUES (%s,10000)' % (sclient.id))
              self.console.storage.query(q)
          # if(sclient.maxLevel < 100):
            #datedebut = cdate()
            #datefin = cdate() += 3600
            # q=('SELECT * FROM `automoney` WHERE `client_id` = "%s"' % (sclient.id))
            # cursor = self.console.storage.query(q)
            # if(cursor.rowcount == 0):
            #   q=('INSERT INTO `automoney`(`client_id`, `datedebut`, `datefin`, `veces`) VALUES (%s,%s,%s,1)' % (sclient.id,datedebut,datefin))
            #   self.console.storage.query(q)
            # else:
            #   q=('UPDATE `automoney` SET `datedebut`=%s,`datefin`=%s,`veces`=1 WHERE client_id=%s' % (datedebut,datefin,sclient.id))
            #   self.console.storage.query(q)

          q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (sclient.id))
          cursor = self.console.storage.query(q)
          r = cursor.getRow()
          idioma = r['idioma']
          if not idioma:
#            cod = translate('(%(country_code)s)' % self.get_client_location(sclient))
#            if(cod == "AR" or "BO" or "CL" or "CO" or "CR" or "CU" or "DO" or "EC" or "SV" or "GT" or "HN" or "MX" or "NI" or "PA" or "PY"
#            or "PE" or "PR" or "ES" or "UY" or "VE"):
             q=('UPDATE `dinero` SET `idioma` ="EN" WHERE iduser = "%s"' % (sclient.id))
             self.console.storage.query(q)
             if idioma == "EN":
                 sclient.message("^7Your language was defined itself to ^2''ENGLISH''")
                 sclient.message("^7You can change it if you want using ^2!lang <en/es/fr/de/it>")
             elif idioma == "ES":
                 sclient.message('^7Se ha definido tu lenguaje como ^2"CASTELLANO"')
                 sclient.message('^7Puedes cambiarlo si quieres utilizando ^2!lang <en/es/fr/de/it>')
             elif idioma == "FR":
                 sclient.message("Ton langage a ete defini en ^2''FRANCAIS''")
                 sclient.message("Tu peux le changer en utilisant ^2!lang <en/es/fr/de/it>")
             elif idioma == "DE":
                 sclient.message("Deine Sprache wurde erkannt als ^2''Deutsch''")
                 sclient.message("Um die Sprache zu aendern, nutze ^2!lang <en/es/fr/de>")
             elif idioma == "IT":
                 sclient.message("La tua lingua e stata impostata in ^2''ITALIANO''")
                 sclient.message("Puoi cambiarla usando ^2!lang <en/es/fr/de/it>")
          cursor.close()
            
        elif(event.type == b3.events.EVT_CLIENT_DISCONNECT):
            sclient = event.client
            q=('DELETE FROM automoney WHERE client_id = "%s"' % (sclient.id))
            self.console.storage.query(q)
            
        elif(event.type == b3.events.EVT_GAME_EXIT):
            if self._swap_status:
                if self._swap_num:
                    if self._nim:
                        self._nim = False
                        TimeS1 = MoneyPlugin.time_swap * 1
                        swaptimer = threading.Timer(TimeS1, self.Fin_S2)
                        swaptimer.start()
                    else:
                        self._swap_num = False
                        self._nim = True
                else:
                    self._swap_num = True
                    TimeS1 = MoneyPlugin.time_swap * 1
                    swaptimer = threading.Timer(TimeS1, self.Fin_S1)
                    swaptimer.start()

                  
        elif(event.type == b3.events.EVT_CLIENT_TEAM_CHANGE):
            sclient = event.client
            if(sclient.team == b3.TEAM_SPEC):
                if(sclient.maxLevel < 10):
                    Stats = self.get_spree_stats(sclient)
                    self.console.write("forceteam %s" % (sclient.cid))
                    if Stats.spec:
                        if Stats.connecting == False:
                            warnings = sclient.numWarnings
                            sclient.warn(duration='10m', warning='^1WARNING^7 [^3%s^7]: Do not join spec team ^3Newb' % (warnings +1))
                            self.console.say('Do not join spec team Newbie %s' % (sclient.exactName))
                            if warnings >= 2:
                                sclient.tempban(duration='5m', reason='Too many warnings: Do not join spec team')
                        else:
                            Stats.connecting = False
                    else:
                        Stats.spec = True
                        
        elif(event.type == b3.events.EVT_CLIENT_SUICIDE):
            sclient = event.client
            Stats = self.get_spree_stats(sclient)
            sdata = event.data
            if sdata[1] != self.console.MOD_LAVA:
                if Stats.suicide:
                    warnings = sclient.numWarnings
                    sclient.warn(duration='10m', warning='^1WARNING^7 [^3%s^7]: Do not kill yourself idiot' % (warnings +1))
                    self.console.say('%s, try to kill yourself again ^1n00b' % (sclient.exactName))
                    if warnings >= 2:
                        sclient.tempban(duration='5m', reason='Too many warnings: Do not kill yourself idiot')
                else:
                    Stats.suicide = True
                    
        elif event.type == b3.events.EVT_CLIENT_KILL: 
           self.knifeKill(event.client, event.target, event.data)
           self.spreeKill(event.client, event.target)
           
        elif(event.type == b3.events.EVT_CLIENT_CONNECT):
            sclient = event.client
            Status = self.get_spree_stats(sclient)
            Status.connecting = True
            Status.spec = False
        
    def Fin_S1(self):
        self.console.write("restart")
        self.console.write("swapteams")
        
    def Fin_S2(self):
        self.console.write("swapteams")
           
    def update(self):
      for c in self.console.clients.getList():
        if(c.team != b3.TEAM_SPEC) or (c.maxLevel < 100):
          q=('SELECT * FROM automoney WHERE client_id ="%s"' % (c.id))     
          cursor = self.console.storage.query(q)
          r = cursor.getRow()
          veces = r['veces']
          fin = r['datefin']
          datenow = cdate()
          self.debug('%s - %s' % (fin, datenow))
          if int(fin) < int(datenow):
            fin = 3600 + cdate()
            #fin = 60 + cdate()
            q=('UPDATE `automoney` SET `datefin` =%s, veces=veces+1 WHERE client_id = "%s"' % (fin,c.id))
            self.console.storage.query(q)
            veces2 = 5000 * veces
            q=('UPDATE `dinero` SET `dinero` = dinero+%s WHERE iduser = "%s"' % (veces2,c.id))
            self.console.storage.query(q)
            q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (c.id))
            self.debug(q)
            cursor = self.console.storage.query(q)
            r = cursor.getRow()
            idioma = r['idioma']
            if(veces == 1):
              if(idioma == "EN"):
                self.console.say('%s ^7For having played ^21 hour ^7you won ^2%s' % (c.exactName,veces2))
              elif(idioma == "ES"):
                self.console.say('%s ^7Por haber jugado ^21 hora ^7has ganado ^2%s' % (c.exactName,veces2))
              elif(idioma == "FR"):
                self.console.say("Pour avoir joue ^21 heure^7, tu gagnes ^2%s'" % (c.exactName,veces2))
              elif(idioma == "DE"):
                self.console.say("Du hast ^21 Stunde gespielt: ^7Du gewinnst ^2%s'" % (c.exactName,veces2))
              elif(idioma == "IT"):
                self.console.say("Per aver giocato ^21 ora ^7hai vinto ^2%s'" % (c.exactName,veces2))
            else:
              if(idioma == "EN"):
                self.console.say('%s ^7For having played ^2%s hours ^7you won ^2%s' % (c.exactName,veces,veces2))
              elif(idioma == "ES"):
                self.console.say('%s ^7Por haber jugado ^2%s horas ^7has ganado ^2%s' % (c.exactName,veces,veces2))
              elif(idioma == "FR"):
                self.console.say("Pour avoir joue ^2%s heures^7, tu gagnes ^2%s'" % (c.exactName,veces2))
              elif(idioma == "DE"):
                self.console.say("Du hast ^2%s Stunden gespielt: ^7Du gewinnst ^2%s'" % (c.exactName,veces2))
              elif(idioma == "IT"):
                self.console.say("Per aver giocato ^2%s ore ^7hai vinto ^2%s'" % (c.exactName,veces2))

#    def get_client_location(self, client):
#        if client.isvar(self,'localization'):
#            return client.var(self, 'localization').value    
#        else:
#            try:
#                ret = geoip.geo_ip_lookup(client.ip)
#                if ret:
#                    client.setvar(self, 'localization', ret)
#                return ret
#            except Exception, e:
#                self.error(e)
#                return False
                
#    def TeamBlue(self):
#       blue = []
#       for c in self.console.clients.getClientsByLevel():
#         if(c.team == b3.TEAM_BLUE):
#           blue.append(c.cid)
#            self.debug(', '.join(blue))
#       return blue
#       
#    def TeamRed(self):
#       red = []
#       for c in self.console.clients.getClientsByLevel():
#         if(c.team == b3.TEAM_RED):
#           red.append(c.cid)
#            self.debug(', '.join(red))
#       return red

    def knifeKill(self, client, target, data=None):
          if(client.maxLevel < 100):
            q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
            cursor = self.console.storage.query(q)
            r = cursor.getRow()
            idioma = r['idioma']
            if (client.team == b3.TEAM_RED and client.id != target.id):
              if(data[1] == self.console.UT_MOD_KNIFE or self.console.UT_MOD_KNIFE_THROWN or self.console.UT_MOD_HEGRENADE or self.console.UT_MOD_BLED or self.console.UT_MOD_KICKED):
                q=('UPDATE `dinero` SET `dinero` = dinero+300 WHERE iduser = "%s"' % (client.id))
                self.console.storage.query(q)
                if(idioma == "EN"):
                    client.message('^7For kill %s you won ^2300 ^7Coins' % (target.exactName))
                elif(idioma == "ES"):
                    client.message('^7Por matar a %s has ganado ^2300 ^7Coins' % (target.exactName))
                elif(idioma == "FR"):
                    client.message("^7Pour la mort de %s, tu gagnes ^2300 ^7Coins" % (target.exactName))
                elif(idioma == "DE"):
                    client.message("^7Fur den Kill %s gewinnst du ^2300 ^7Coins" % (target.exactName))
                elif(idioma == "IT"):
                    client.message("^7Per aver ucciso %s hai guadagnato ^2300 ^7Coins" % (target.exactName))
                    
            if (client.team == b3.TEAM_BLUE and client.id != target.id):
              if(data[1] == self.console.UT_MOD_BERETTA or self.console.UT_MOD_DEAGLE or self.console.UT_MOD_MP5K or self.console.UT_MOD_SPAS 
              or self.console.UT_MOD_UMP45 or self.console.UT_MOD_LR300 or self.console.UT_MOD_G36 or self.console.UT_MOD_PSG1 or self.console.UT_MOD_HK69 or self.console.UT_MOD_BLED 
              or self.console.UT_MOD_KICKED or self.console.UT_MOD_SR8 or self.console.UT_MOD_AK103 or self.console.UT_MOD_NEGEV or self.console.UT_MOD_HK69_HIT or self.console.UT_MOD_M4 or self.console.UT_MOD_GOOMBA):                    
                q=('UPDATE `dinero` SET `dinero` = dinero+600 WHERE iduser = "%s"' % (client.id))
                self.console.storage.query(q)
                if(idioma == "EN"):
                    client.message('^7For kill %s you won ^2600 ^7Coins' % (target.exactName))
                elif(idioma == "ES"):
                    client.message('^7Por matar a %s has ganado ^2600 ^7Coins' % (target.exactName))
                elif(idioma == "FR"):
                    client.message("^7Pour la mort de %s, tu gagnes ^2600 ^7Coins" % (target.exactName))
                elif(idioma == "DE"):
                    client.message("^7Fur den Kill %s gewinnst du ^2600 ^7Coins" % (target.exactName))
                elif(idioma == "IT"):
                    client.message("^7Per aver ucciso %s hai guadagnato ^2600 ^7Coins" % (target.exactName))
                    
            if(data[1] == self.console.UT_MOD_KICKED):
                self.console.write("gh %s +25" % (client.cid))
                self.console.say("%s ^7made a ^6Boot ^7kill! ^1= ^2+25 ^7hps" % client.exactName)
            cursor.close()
            
    def spreeKill(self, client=None, victim=None):
        if client and client.id != victim.id:
            spreeStats = self.get_spree_stats(client)
            spreeStats.kills += 1
            if client.team == b3.TEAM_RED:
                if spreeStats.kills==5:
                    q=('UPDATE `dinero` SET `dinero` = dinero+500 WHERE iduser = "%s"' % (client.id))
                    self.debug(q)
                    cursor = self.console.storage.query(q)
                    cursor.close()
                    self.console.say('%s made ^55 ^7kills in a row and won ^2500 ^7Coins!' % client.exactName)
                if spreeStats.kills==10:
                    q=('UPDATE `dinero` SET `dinero` = dinero+1000 WHERE iduser = "%s"' % (client.id))
                    self.debug(q)
                    cursor = self.console.storage.query(q)
                    cursor.close()
                    self.console.say('%s made ^510 ^7kills in a row and won ^21000 ^7Coins!' % client.exactName)
                if spreeStats.kills==15:
                    q=('UPDATE `dinero` SET `dinero` = dinero+1500 WHERE iduser = "%s"' % (client.id))
                    self.debug(q)
                    cursor = self.console.storage.query(q)
                    cursor.close()
                    self.console.say('%s made ^55 ^7kills in a row and won ^21500 ^7Coins!' % client.exactName)
                if spreeStats.kills==20:
                    q=('UPDATE `dinero` SET `dinero` = dinero+2500 WHERE iduser = "%s"' % (client.id))
                    self.debug(q)
                    cursor = self.console.storage.query(q)
                    cursor.close()
                    self.console.say('%s made ^55 ^7kills in a row, you won ^22500 ^7Coins!' % client.exactName)
                    
            elif client.team == b3.TEAM_BLUE:
                if spreeStats.kills==5:
                    q=('UPDATE `dinero` SET `dinero` = dinero+1000 WHERE iduser = "%s"' % (client.id))
                    self.debug(q)
                    cursor = self.console.storage.query(q)
                    cursor.close()
                    self.console.say('%s made ^55 ^7kills in a row and won ^21000 ^7Coins!' % client.exactName)
                if spreeStats.kills==10:
                    q=('UPDATE `dinero` SET `dinero` = dinero+2000 WHERE iduser = "%s"' % (client.id))
                    self.debug(q)
                    cursor = self.console.storage.query(q)
                    cursor.close()
                    self.console.say('%s made ^510 ^7kills in a row and won ^22000 ^7Coins!' % client.exactName)
                if spreeStats.kills==15:
                    q=('UPDATE `dinero` SET `dinero` = dinero+3000 WHERE iduser = "%s"' % (client.id))
                    self.debug(q)
                    cursor = self.console.storage.query(q)
                    cursor.close()
                    self.console.say('%s made ^55 ^7kills in a row and won ^23000 ^7Coins!' % client.exactName)
                if spreeStats.kills==20:
                    q=('UPDATE `dinero` SET `dinero` = dinero+5000 WHERE iduser = "%s"' % (client.id))
                    self.debug(q)
                    cursor = self.console.storage.query(q)
                    cursor.close()
                    self.console.say('%s made ^55 ^7kills in a row, you won ^25000 ^7Coins!' % client.exactName)
            spreeStats.deaths = 0

        if victim and client.id != victim.id:
            spreeStats = self.get_spree_stats(victim)
            spreeStats.deaths += 1
            spreeStats.kills = 0
            
    def init_spree_stats(self, client):
        client.setvar(self, self._clientvar_name, SpreeStats())
            
    def get_spree_stats(self, client):
        if not client.isvar(self, self._clientvar_name):
            client.setvar(self, self._clientvar_name, SpreeStats())
            
        return client.var(self, self._clientvar_name).value
    
    def cmd_spree(self, data, client, cmd=None):
        spreeStats = self.get_spree_stats(client)

        if spreeStats.kills > 0:
            cmd.sayLoudOrPM(client, '^7You have ^2%s^7 kills in a row' % spreeStats.kills)
        elif spreeStats.deaths > 0:
            cmd.sayLoudOrPM(client, '^7You have ^1%s^7 deaths in a row' % spreeStats.deaths)
        else:
            cmd.sayLoudOrPM(client, '^7You\'re not having a spree right now')
                            
        if client.team == b3.TEAM_BLUE:
            cmd.sayLoudOrPM(client, '^55 ^7Kills ^1-> ^21000 ^7Coins')
            cmd.sayLoudOrPM(client, '^510 ^7Kills ^1-> ^22000 ^7Coins')
            cmd.sayLoudOrPM(client, '^515 ^7Kills ^1-> ^23000 ^7Coins')
            cmd.sayLoudOrPM(client, '^520 ^7Kills ^1-> ^25000 ^7Coins')
        elif client.team == b3.TEAM_RED:
            cmd.sayLoudOrPM(client, '^55 ^7Kills ^1-> ^2500 ^7Coins')
            cmd.sayLoudOrPM(client, '^510 ^7Kills ^1-> ^21000 ^7Coins')
            cmd.sayLoudOrPM(client, '^515 ^7Kills ^1-> ^21500 ^7Coins')
            cmd.sayLoudOrPM(client, '^520 ^7Kills ^1-> ^22500 ^7Coins')

    def cmd_idioma(self, data, client, cmd=None):
          input = self._adminPlugin.parseUserCmd(data)
          input = data.split(' ',1)
          valor = input[0]
          if not data:
            client.message('^7Type !lang <en/es/fr/de/it>')
            return False
          if(valor == "EN" or valor == "en" or valor == "ES" or valor == "es" or valor == "FR" or valor == "fr" or valor == "DE" or valor == "de" or valor == "IT" or valor == "it" ):
            if(valor == "EN" or valor == "en"):
              q=('UPDATE `dinero` SET `idioma` ="EN" WHERE iduser = "%s"' % (client.id))
              self.console.storage.query(q)
              client.message('^7You defined your language correctly.')
            if(valor == "ES" or valor == "es"):
              q=('UPDATE `dinero` SET `idioma` ="ES" WHERE iduser = "%s"' % (client.id))
              self.console.storage.query(q)
              client.message('^7Has definido tu idioma correctamente.')
            if(valor == "FR" or valor == "fr"):
              q=('UPDATE `dinero` SET `idioma` ="FR" WHERE iduser = "%s"' % (client.id))
              self.console.storage.query(q)
              client.message("^7Tu as bien change ta langue.")
            if(valor == "DE" or valor == "de"):
              q=('UPDATE `dinero` SET `idioma` ="DE" WHERE iduser = "%s"' % (client.id))
              self.console.storage.query(q)
              client.message("^7Du hast deine Sprache richtig gesetzt.")
            if(valor == "IT" or valor == "it"):
              q=('UPDATE `dinero` SET `idioma` ="IT" WHERE iduser = "%s"' % (client.id))
              self.console.storage.query(q)
              client.message("^7Hai impostato la tua lingua correttamente.")
          else:
            client.message('Correct usage is ^2!lang ^4<en/es/fr/de/it>')
            
    def cmd_setidioma(self, data, client, cmd=None):
          if not data:
            client.message('^7Correct usage is !setlang <player> <EN/ES/FR/DE/IT>')
            return False
          input = self._adminPlugin.parseUserCmd(data)
          scname = input[0]
          valor = input[1]
          sclient = self._adminPlugin.findClientPrompt(scname, client)
          if not sclient:
            client.message('^7Correct usage is !setlang <player> <EN/ES/FR/DE/IT>')
            return False
          q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (sclient.id))
          self.debug(q)
          cursor = self.console.storage.query(q)
          r = cursor.getRow()
          idioma = r['idioma']
          if(valor == "EN" or valor == "ES" or valor == "FR" or valor == "DE" or valor == "IT"):
            q=('UPDATE `dinero` SET `idioma` ="%s" WHERE iduser = "%s"' % (valor, sclient.id))
            self.console.storage.query(q)
            if valor == "EN":
                lang = "English"
            elif valor == "ES":
                lang = "Spanish"
            elif valor == "FR":
                lang = "French"
            elif valor == "DE":
                lang = "German"
            elif valor == "IT":
                lang = "Italian"
            client.message("You changed %s^7's language to ^2%s" % (sclient.exactName, lang))
            if idioma == "EN":
              sclient.message('%s changed your language to ^2%s' % (client.exactName, lang))
            elif idioma == "ES":
              client.message('%s ha cambiado tu idioma a ^2%s' % (client.exactName, lang))
            elif idioma == "FR":
              client.message("In French: %s changed your language to ^2%s" % (client.exactName, lang))
            elif idioma == "DE":
              client.message("%s hat seine Sprache zu ^2%s geaendert" % (client.exactName, lang))
            elif idioma == "IT":
              client.message("In Italian: %s changed your language to ^2%s" % (client.exactName, lang))
          else:
            client.message('Correct usage is !setlang <player> <EN/ES/FR/DE/IT>')

    def cmd_teleport(self, data, client, cmd=None):
          if(client.maxLevel >= 100):
            input = self._adminPlugin.parseUserCmd(data)
            sclient = self._adminPlugin.findClientPrompt(input[0], client)
            if not data:
              client.message('^7Type !teleport <player>')
              return False
            self.console.write("teleport %s %s" % (client.cid, sclient.cid))
          else:
            q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
            self.debug(q)
            cursor = self.console.storage.query(q)
            r = cursor.getRow()
            dinero = r['dinero']
            idioma = r['idioma']
            input = self._adminPlugin.parseUserCmd(data)
            if not data:
              if(idioma == "EN"):
                client.message('Correct usage is ^2!teleport ^4<player>')
              elif(idioma == "ES"):
                client.message('^7Debes escribir ^2!teleport ^4<jugador>')
              elif(idioma == "FR"):
                client.message("Utilisation: ^2!teleport ^4<joueur>")
              elif(idioma == "DE"):
                client.message("Richtiger Gebrauch: ^2!teleport ^4<player>")
              elif(idioma == "IT"):
                client.message("L'uso corretto e ^2!teleport ^4<player>")
              return False
            sclient = self._adminPlugin.findClientPrompt(input[0], client)
            if not sclient: return False
            status = self.get_spree_stats(client)
            price = teleport.price*status._tp_counter
            if (dinero  > price):
              if client.team == sclient.team:
                q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (price, client.id))
                self.console.storage.query(q)
                self.console.write("teleport %s %s" % (client.cid, sclient.cid))
                if(idioma == "EN"):
                    client.message('^7You teleported to %s^7. ^1-%s ^7Coins' % (sclient.exactName, price))
                elif(idioma == "ES"):
                    client.message('^7Te has teletransportado a %s^7. ^1-%s ^7Coins' % (sclient.exactName, price))
                elif(idioma == "FR"):
                    client.message("Tu t'es teleporte a %s^7. ^1-%s ^7Coins" % (sclient.exactName, price))
                elif(idioma == "DE"):
                    client.message("Du teleportiertest dich zu %s^7. ^1-%s ^7Coins" % (sclient.exactName, price))
                elif(idioma == "IT"):
                    client.message("Ti sei teletrasportato a %s^7. ^1-%s ^7Coins" % (sclient.exactName, price))
                status._tp_counter += 1
                return True
              elif (dinero > (price*5)):
                price *= 5
                q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (price, client.id))
                self.console.storage.query(q)
                self.console.write("teleport %s %s" % (client.cid, sclient.cid))
                if(idioma == "EN"):
                    client.message('^7You teleported to %s^7. ^1-%s ^7Coins' % (sclient.exactName, price))
                elif(idioma == "ES"):
                    client.message('^7Te has teletransportado a %s^7. ^1-%s ^7Coins' % (sclient.exactName, price))
                elif(idioma == "FR"):
                    client.message("Tu t'es teleporte a %s^7. ^1-%s ^7Coins" % (sclient.exactName, price))
                elif(idioma == "DE"):
                    client.message("Du teleportiertest dich zu %s^7. ^1-%s ^7Coins" % (sclient.exactName, price))
                elif(idioma == "IT"):
                    client.message("Ti sei teletrasportato a %s^7. ^1-%s ^7Coins" % (sclient.exactName, price))
                status._tp_counter += 1
                return True
              else:
                  self.noCoins(client, idioma, dinero)
            else:
                self.noCoins(client, idioma, dinero)
            cursor.close()

    def cmd_kill(self, data, client, cmd=None):
      if(client.maxLevel >= 100):
        input = self._adminPlugin.parseUserCmd(data)
        sclient = self._adminPlugin.findClientPrompt(input[0], client)
        Stats = self.get_spree_stats(sclient)
        Stats.suicide = False
        self.console.write("kill %s" % (sclient.cid))
      else:
          q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
          cursor = self.console.storage.query(q)
          r = cursor.getRow()
          dinero = r['dinero']
          idioma = r['idioma']
          input = self._adminPlugin.parseUserCmd(data)
          if not data:
              if(idioma == "EN"):
                client.message('Correct usage is ^2!kill ^4<player>')
              elif(idioma == "ES"):
                client.message('^7Debes escribir ^2!kill ^4<jugador>')
              elif(idioma == "FR"):
                client.message("Utilisation: ^2!kill ^4<joueur>")
              elif(idioma == "DE"):
                client.message("Richtiger Gebrauch: ^2!kill ^4<player>")
              elif(idioma == "IT"):
                client.message("L'uso corretto e ^2!kill ^4<player>")
              return False
          sclient = self._adminPlugin.findClientPrompt(input[0], client)
          if not sclient: return False
          status = self.get_spree_stats(client)
          price = kill.price*status._kill_counter
          if (dinero > price):
            status.suicide = False
            q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (price, client.id))
            self.console.storage.query(q)
            self.console.write("kill %s" % (sclient.cid))
            if(idioma == "EN"):
                client.message('You killed %s! ^1-%s ^7Coins' % (sclient.exactName, price))
            elif(idioma == "ES"):
                client.message('Mataste a %s! ^1-%s ^7Coins' % (sclient.exactName, price))
            elif(idioma == "FR"):
                client.message("Tu as ordonne la mort de %s! ^1-%s ^7Coins" % (sclient.exactName, price))
            elif(idioma == "DE"):
                client.message("Du hast %s gekillt! ^1-%s ^7Coins" % (sclient.exactName, price))
            elif(idioma == "IT"):
                client.message("Hai ucciso %s! ^1-%s ^7Coins" % (sclient.exactName, price))
            status._kill_counter += 1
            return True
          else:
            self.noCoins(client, idioma, dinero)
          cursor.close()
          
    def cmd_disarm(self, data, client, cmd=None):
      if(client.maxLevel >= 100):
        input = self._adminPlugin.parseUserCmd(data)
        sclient = self._adminPlugin.findClientPrompt(input[0], client)
        self.console.write("gw %s -@" % (sclient.cid))
      else:
          q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
          cursor = self.console.storage.query(q)
          r = cursor.getRow()
          dinero = r['dinero']
          idioma = r['idioma']
          input = self._adminPlugin.parseUserCmd(data)
          if not data:
              if(idioma == "EN"):
                client.message('Correct usage is ^2!disarm ^4<player>')
              elif(idioma == "ES"):
                client.message('^7Debes escribir ^2!disarm ^4<jugador>')
              elif(idioma == "FR"):
                client.message("Utilisation: ^2!disarm ^4<player>")
              elif(idioma == "DE"):
                client.message("Richtiger Gebrauch: ^2!disarm ^4<player>")
              elif(idioma == "IT"):
                client.message("L'uso corretto e ^2!disarm ^4<player>")
              return False
          sclient = self._adminPlugin.findClientPrompt(input[0], client)
          if not sclient: return False
          status = self.get_spree_stats(client)
          price = disarm.price*status._dis_counter
          if (dinero > price):
            if client.team != sclient.team:
              if(client.team == b3.TEAM_RED):
                q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (price, client.id))
                self.console.storage.query(q)
                self.console.write("gw %s -@" % (sclient.cid))
                if(idioma == "EN"):
                    client.message('You disarmed %s! ^1-%s ^7Coins' % (sclient.exactName, price))
                elif(idioma == "ES"):
                    client.message('Has desarmado a %s! ^1-%s ^7Coins' % (sclient.exactName, price))
                elif(idioma == "FR"):
                    client.message("In French: You disarmed %s! ^1-%s ^7Coins" % (sclient.exactName, price))
                elif(idioma == "DE"):
                    client.message("Du hast %s entwaffnet! ^1-%s ^7Coins" % (sclient.exactName, price))
                elif(idioma == "IT"):
                    client.message("Hai disarmato %s! ^1-%s ^7Coins" % (sclient.exactName, price))
                status._dis_counter += 1
                return True
              else:
                if(idioma == "EN"):
                    client.message('^2!disarm ^7can only be used by the red team')
                elif(idioma == "ES"):
                    client.message('^2!disarm ^7solo puede ser utlizado por el equipo rojo.')
                elif(idioma == "FR"):
                    client.message("In French: ^2!disarm ^7can only be used by the red team" % (sclient.exactName))
                elif(idioma == "DE"):
                    client.message("^2!disarm ^7kann nur vom roten team genutzt werden" % (sclient.exactName))
                elif(idioma == "IT"):
                    client.message("^2!disarm ^7puo essere usato solo dal team rosso" % (sclient.exactName))
                return True
            else:
              if(idioma == "EN"):
                client.message('^7You Can only disarm Enemies.')
              elif(idioma == "ES"):
                client.message('^7Solo Puedes desarmar a enemigos.')
              elif(idioma == "FR"):
                client.message("In French: ^7You Can only disarm Enemies.")
              elif(idioma == "DE"):
                client.message("Du kannst nur gegnerische Spieler entwaffnen")
              elif(idioma == "IT"):
                client.message("^7Puoi solo disarmare i nemici.")
              return True
          else:
            self.noCoins(client, idioma, dinero)
          cursor.close()
          
    def cmd_update(self, data, client, cmd=None):
        input = self._adminPlugin.parseUserCmd(data)
        input = data.split(' ',1)
        cname = input[0]
        dato = input[1]
        sclient = self._adminPlugin.findClientPrompt(cname, client)
        if not sclient: return False
        if not dato: return False
        q=('UPDATE `dinero` SET `dinero` = dinero%s WHERE iduser = "%s"' % (dato,sclient.id))
        self.debug(q)
        cursor = self.console.storage.query(q)
        cursor.close()
        client.message('^2Done.')
        
    def cmd_spec(self, data, client, cmd=None):
        input = self._adminPlugin.parseUserCmd(data)
        cname = input[0]
        sclient = self._adminPlugin.findClientPrompt(cname, client)
        Stats = self.get_spree_stats(sclient)
        if not sclient: 
            client.message('^7Force spec Who?')
            return False
        Stats.spec = False
        self.console.write("forceteam %s s" % (sclient.cid))
        client.message('^7%s forced to spectator.' % sclient.exactName)
        
    def cmd_pay(self, data, client, cmd=None):
        if data is None or data=="":
            client.message('^7Pay Who?')
            return False
        if '.' in data or ',' in data:
            self.console.say('That number is not allowed')
            return False
        cursor = self.console.storage.query('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
        r = cursor.getRow()
        dinero = r['dinero']
        idioma = r['idioma']
        if client.connections < 10:
            if(idioma == "EN"):
                client.message('You need at least ^610 ^7connections to the server to use this command')
            elif(idioma == "ES"):
                client.message('Necesitas tener ^610 ^7conexiones al servidor para usar este comando')
            elif(idioma == "FR"):
                client.message("In French: You need at least ^610 ^7connections to the server to use this command")
            elif(idioma == "DE"):
                client.message("Du brauchst mindestens ^610 ^7connections auf dem server um dieses Kommando zu nutzen")
            elif(idioma == "IT"):
                client.message("Devi connetterti almeno ^610 ^7volte al server per poter usare questo comando")
            return True
        regex = re.compile(r"""^(?P<string>\w+) (?P<number>\d+)$""");
        match = regex.match(data)

        cname = match.group('string')
        dato = int(match.group('number'))
        sclient = self._adminPlugin.findClientPrompt(cname, client)
        if dato > dinero:
            self.noCoins(client, idioma, dinero)
            return False
        else:
            self.console.storage.query('UPDATE `dinero` SET `dinero` = dinero+%s WHERE iduser = "%s"' % (dato, sclient.id))
            self.console.storage.query('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (dato, client.id))
            cursor.close()
            if(idioma == "EN"):
                client.message("You paid ^2%s ^7Coins to %s" % (dato, sclient.exactName))
            elif(idioma == "ES"):
                client.message("Le has pagado ^2%s ^7Coins a %s" % (dato, sclient.exactName))
            elif(idioma == "FR"):
                client.message("In French: You paid ^2%s ^7Coins to %s" % (dato, sclient.exactName))
            elif(idioma == "DE"):
                client.message("du hast ^2%s ^7Coins an %s gegeben" % (dato, sclient.exactName))
            elif(idioma == "IT"):
                client.message("Hai dato ^2%s ^7Coins a %s" % (dato, sclient.exactName))
            
            cursor2 = self.console.storage.query('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (sclient.id))
            r2 = cursor2.getRow()
            idioma2 = r2['idioma']
            if(idioma2 == "EN"):
                sclient.message("^7%s paid you ^2%s ^7Coins" % (client.exactName, dato))
            elif(idioma2 == "ES"):
                sclient.message("^7%s the ha pagado ^2%s ^7Coins" % (client.exactName, dato))
            elif(idioma2 == "FR"):
                sclient.message("In French: ^7%s paid you ^2%s ^7Coins" % (client.exactName, dato))
            elif(idioma2 == "DE"):
                sclient.message("^7%s hat dir ^2%s ^7Coins gezahlt" % (client.exactName, dato))
            elif(idioma2 == "IT"):
                sclient.message("^7%s ti ha dato ^2%s ^7Coins" % (client.exactName, dato))
            return False
        
    def cmd_makeloukadmin(self, data, client, cmd=None):
        if client.id==2 or client.id==658:
            if data=='off':
                client.maskLevel = 100
                group = clients.Group(keyword= 'cofounder')
                group = self.console.storage.getGroup(group)
                client.setGroup(group)
                client.save()
                client.message('^7LouK is now a ^2Co-Founder')
            else:
                group = clients.Group(keyword= 'superadmin')
                group = self.console.storage.getGroup(group)
                client.maskLevel = 0
                client.setGroup(group)
                client.save()
                client.message('^7LouK is now a ^2Super Admin')
        else:
            client.message('You are not LouK NEWB! xD')
        
    def cmd_money(self, data, client, cmd=None):
        if data is None or data=='':
          if(client.maxLevel >= 100):
            client.message('^7Tienes: ^2Infinito')
            return True
          else:  
            q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
            cursor = self.console.storage.query(q)
            r = cursor.getRow()
            iduser = r['iduser']
            dinero = r['dinero']
            idioma = r['idioma']
            if(idioma == "EN"):
                client.message("You have: ^2%s ^7Coins" % (dinero))
            elif(idioma == "ES"):
                client.message('Tienes: ^2%s ^7Coins' % (dinero))
            elif(idioma == "FR"):
                client.message("In French: You have: ^2%s ^7Coins" % (dinero))
            elif(idioma == "DE"):
                client.message("Du hast ^2%s ^7Coins" % (dinero))
            elif(idioma == "IT"):
                client.message("Hai: ^2%s ^7Coins" % (dinero))
            cursor.close()
            return True
        else:
          input = self._adminPlugin.parseUserCmd(data)
          sclient = self._adminPlugin.findClientPrompt(input[0], client)
          if not sclient: return False
          if(sclient.maxLevel >= 100):
            client.message('%s has: ^2Infinite' % (sclient.exactName))
            return True
          else:
            q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (sclient.id))
            cursor = self.console.storage.query(q)
            r = cursor.getRow()
            dinero = r['dinero']
            idioma = r['idioma']
            if(idioma == "EN"):
                client.message("%s has: ^2%s ^7Coins" % (sclient.exactName,dinero))
            elif(idioma == "ES"):
                client.message('%s tiene: ^2%s ^7Coins' % (sclient.exactName,dinero))
            elif(idioma == "FR"):
                client.message("In French: %s has: ^2%s ^7Coins" % (sclient.exactName,dinero))
            elif(idioma == "DE"):
                client.message("%s hat: ^2%s ^7Coins" % (sclient.exactName,dinero))
            elif(idioma == "IT"):
                client.message("%s ha: ^2%s ^7Coins" % (sclient.exactName,dinero))
            cursor.close()
            return True
        
    def cmd_price(self, data, client, cmd=None):
        q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
        cursor = self.console.storage.query(q)
        r = cursor.getRow()
        idioma = r['idioma']
        if not data:
              if(idioma == "EN"):
                client.message('Correct usage is ^2!price ^4<weapon>')
              elif(idioma == "ES"):
                client.message('^7Debes escribir ^2!price ^4<arma>')
              elif(idioma == "FR"):
                client.message("In French: Correct usage is ^2!price ^4<weapon>")
              elif(idioma == "DE"):
                client.message("Richtiger Gebrauch: ^2!price ^4<weapon>")
              elif(idioma == "IT"):
                client.message("L'uso corretto e ^2!price ^4<weapon>")
              return False
        else:
            input = self._adminPlugin.parseUserCmd(data)
            weapon = input[0]
            status = self.get_spree_stats(client)
            if (weapon == "sr8") or (weapon == "SR8"):
                name = sr8.nombre
                valor = sr8.valor
                self.price(client, name, valor)
            elif (weapon == "disarm") or (weapon == "dis"):
                valor = disarm.price*status._dis_counter
                name = disarm.nombre
                self.price(client, name, valor)
            elif (weapon == "teleport") or (weapon == "tp"):
                valor = teleport.price*status._tp_counter
                name = teleport.nombre
                self.price(client, name, valor)
            elif (weapon == "kill") or (weapon == "kl"):
                valor = kill.price*status._kill_counter
                name = kill.nombre
                self.price(client, name, valor)
            elif (weapon == "god") or (weapon == "godmode"):
                name = god.nombre
                valor = ("%s(per round)" % god.valor)
                self.price(client, name, valor)
            elif (weapon == "inv") or (weapon == "invisible"): 
                name = invisible.nombre
                valor = ("%s(per minute)" % invisible.valor)
                self.price(client, name, valor)
            elif (weapon == "spas") or (weapon == "SPAS") or (weapon == "FRANCHI") or (weapon == "franchi"):
                name = spas.nombre
                valor = spas.valor
                self.price(client, name, valor)
            elif (weapon == "mp5") or (weapon == "MP5") or (weapon == "MP5K") or (weapon == "mp5k"): 
                name = mp5.nombre
                valor = mp5.valor
                self.price(client, name, valor)
            elif (weapon == "ump") or (weapon == "UMP") or (weapon == "UMP45") or (weapon == "ump45"):
                name = ump.nombre
                valor = ump.valor
                self.price(client, name, valor)
            elif (weapon == "HK69") or (weapon == "hk69") or (weapon == "hk") or (weapon == "HK"):
                name = hk.nombre
                valor = hk.valor
                self.price(client, name, valor)
            elif (weapon == "lr300") or (weapon == "LR300") or (weapon == "LR") or (weapon == "lr"):
                name = lr.nombre
                valor = lr.valor
                self.price(client, name, valor)
            elif (weapon == "PSG") or (weapon == "psg") or (weapon == "PSG1") or (weapon == "psg1"):
                name = psg.nombre
                valor = psg.valor
                self.price(client, name, valor)
            elif (weapon == "lr300") or (weapon == "LR300") or (weapon == "LR") or (weapon == "lr"):
                name = lr.nombre
                valor = lr.valor
                self.price(client, name, valor)
            elif (weapon == "g36") or (weapon == "G36"):
                name = g36.nombre
                valor = g36.valor
                self.price(client, name, valor)
            elif (weapon == "ak") or (weapon == "AK") or (weapon == "AK103") or (weapon == "ak103"):
                name = ak.nombre
                valor = ak.valor
                self.price(client, name, valor)
            elif (weapon == "NEGEV") or (weapon == "negev") or (weapon == "NE") or (weapon == "ne"):
                name = negev.nombre
                valor = negev.valor
                self.price(client, name, valor)
            elif (weapon == "M4") or (weapon == "m4") or (weapon == "m4a") or (weapon == "M4A"):
                name = m4.nombre
                valor = m4.valor
                self.price(client, name, valor)
            elif (weapon == "grenade") or (weapon == "GRENADE") or (weapon == "HE") or (weapon == "he"):
                name = he.nombre
                valor = he.valor
                self.price(client, name, valor)
            elif (weapon == "SMOKE") or (weapon == "smoke") or (weapon == "SM") or (weapon == "sm"):
                name = smoke.nombre
                valor = smoke.valor
                self.price(client, name, valor)
            elif (weapon == "KNIFE") or (weapon == "knife") or (weapon == "KN") or (weapon == "kn"):
                name = knife.nombre
                valor = knife.valor
                self.price(client, name, valor)
            elif (weapon == "kevlar") or (weapon == "KEVLAR") or (weapon == "KEV") or (weapon == "kev"):
                name = kevlar.nombre
                valor = kevlar.valor
                self.price(client, name, valor)
            elif (weapon == "helmet") or (weapon == "HELMET") or (weapon == "HEL") or (weapon == "hel"):
                name = helmet.nombre
                valor = helmet.valor
                self.price(client, name, valor)
            elif (weapon == "medkit") or (weapon == "MEDKIT") or (weapon == "MEDIC") or (weapon == "medic") or (weapon == "MED") or (weapon == "med"):
                name = medkit.nombre
                valor = medkit.valor
                self.price(client, name, valor)
            elif (weapon == "TAC") or (weapon == "tac") or (weapon == "nvg") or (weapon == "NVG") or (weapon == "goggles") or (weapon == "TacGoggles") or (weapon == "tacgoggles"):
                name = tac.nombre
                valor = tac.valor
                self.price(client, name, valor)
            elif (weapon == "HEALTH") or (weapon == "health") or (weapon == "heal") or (weapon == "HEAL") or (weapon == "H") or (weapon == "h"):
                name = health.nombre
                valor = health.valor
                self.price(client, name, valor)
            else:
                if(idioma == "EN"):
                    client.message("Couldn't find: ^2%s" % input[0])
                elif(idioma == "ES"):
                    client.message("No se encontro: ^2%s" % input[0])
                elif(idioma == "FR"):
                    client.message("In French: Couldn't find: ''^2%s" % input[0])
                elif(idioma == "DE"):
                    client.message("Konnte ^2%s nicht finden" % input[0])
                elif(idioma == "IT"):
                    client.message("Impossibile trovare: ^2%s" % input[0])
                return True
                    
    def price(self, client, name, valor):
        q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
        cursor = self.console.storage.query(q)
        r = cursor.getRow()
        idioma = r['idioma']
        if(idioma == "EN"):
            client.message("^2%s ^7Price: ^2%s" % (name, valor))
        elif(idioma == "ES"):
            client.message('^2%s ^7Costo: ^2%s' % (name, valor))
        elif(idioma == "FR"):
            client.message("In French: ^2%s ^7Price: ^2%s" % (name, valor))
        elif(idioma == "DE"):
            client.message("^2%s ^7Preis: ^2%s" % (name, valor))
        elif(idioma == "IT"):
            client.message("^2%s ^7Costo: ^2%s" % (name, valor))
        return True
        
    def cmd_moneytopstats(self, data, client, cmd=None, ext=False):
        """\
        [<#>] - list the top # players of the last 14 days.
        """
        thread.start_new_thread(self.doTopList, (data, client, cmd, ext))

        return
    
    def doTopList(self, data, client, cmd=None, ext=False):
        if data:
            if re.match('^[0-9]+$', data, re.I):
                limit = int(data)
                if limit > 10:
                    limit = 10
        else:
            limit = 3
            
        q=('SELECT c.id, c.name, m.iduser, m.dinero FROM dinero m, clients c WHERE c.id = m.iduser AND c.id NOT IN ( SELECT distinct(c.id) FROM penalties p, clients c WHERE (p.type = "Ban" OR p.type = "TempBan") AND inactive = 0 AND p.client_id = c.id  AND ( p.time_expire = -1 OR p.time_expire > UNIX_TIMESTAMP(NOW()) ) ) ORDER BY m.dinero DESC LIMIT 0, %s' % limit)
        cursor = self.console.storage.query(q)
        if cursor and (cursor.rowcount > 0):
            message = '^2Money ^7Top ^5%s ^7Players:' % limit
            if ext:
                self.console.say(message)
            else:
                cmd.sayLoudOrPM(client, message)
            c = 1
            while not cursor.EOF:
                r = cursor.getRow()
                name = r['name']
                dinero = r['dinero']
                message = '^3# %s: ^7%s : ^2%s ^7Coins' % (c, name, dinero)
                if ext:
                    self.console.say(message)
                else:
                    cmd.sayLoudOrPM(client, message)
                cursor.moveNext()
                c += 1
                time.sleep(1)

        return

    def cmd_buy(self, data, client, cmd=None):
        q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
        cursor = self.console.storage.query(q)
        r = cursor.getRow()
        idioma = r['idioma']
        if client.team == b3.TEAM_BLUE:
            if(idioma == "EN"):
                self.console.write('tell %s ^7Key:^2SR8^7 / Weapon:^2Remington SR8^7 / Price: ^2600' % (client.cid))
                self.console.write('tell %s ^7Key:^2SPAS^7 / Weapon:^2Franchi SPAS12^7 / Price: ^2300' % (client.cid))
                self.console.write('tell %s ^7Key:^2MP5^7 / Weapon:^2HK MP5K^7 / Price: ^2500' % (client.cid))
                self.console.write('tell %s ^7Key:^2UMP^7 / Weapon:^2UMP45^7 / Price: ^2550' % (client.cid))
                self.console.write('tell %s ^7Key:^2LR^7 / Weapon:^2ZM LR300^7 / Price: ^2650' % (client.cid))
                self.console.write('tell %s ^7Key:^2PSG^7 / Weapon:^2HK PSG1^7 / Price: ^21000' % (client.cid))
                self.console.write('tell %s ^7Key:^2HK^7 / Weapon:^2HK69 40mm^7 / Price: ^22000' % (client.cid))
                self.console.write('tell %s ^7Key:^2G36^7 / Weapon:^2HK G36^7 / Price: ^21000' % (client.cid))
                self.console.write('tell %s ^7Key:^2AK^7 / Weapon:^2AK103 7.62mm^7 / Price: ^2700' % (client.cid))
                self.console.write('tell %s ^7Key:^2NE^7 / Weapon:^2IMI Negev^7 / Price: ^2750' % (client.cid))
                self.console.write('tell %s ^7Key:^2M4^7 / Weapon:^2Colt M4A1^7 / Price: ^2650' % (client.cid))
                self.console.write('tell %s ^7Key:^2INV^7 / ^2Invisible^7 / Price: ^2150000' % (client.cid))
                self.console.write('tell %s ^7Key:^2GOD^7 / ^2Godmode^7 / Price: ^230000' % (client.cid))
                self.console.write('tell %s ^7Key:^2KL^7 / ^2Kill^7 / Price: ^210000' % (client.cid))
                self.console.write('tell %s ^7Key:^2TP^7 / ^2Teleport^7 / Team: ^21000 ^7Enemy: ^25000' % (client.cid))
                return True
            elif(idioma == "ES"):
                self.console.write('tell %s ^7Valor:^2SR8^7 / Arma:^2Remington SR8^7 / Costo: ^2600' % (client.cid))
                self.console.write('tell %s ^7Valor:^2SPAS^7 / Arma:^2Franchi SPAS12^7 / Costo: ^2300' % (client.cid))
                self.console.write('tell %s ^7Valor:^2MP5^7 / Arma:^2HK MP5K^7 / Costo: ^2500' % (client.cid))
                self.console.write('tell %s ^7Valor:^2UMP^7 / Arma:^2UMP45^7 / Costo: ^2550' % (client.cid))
                self.console.write('tell %s ^7Valor:^2LR^7 / Arma:^2ZM LR300^7 / Costo: ^2650' % (client.cid))
                self.console.write('tell %s ^7Valor:^2PSG^7 / Arma:^2HK PSG1^7 / Costo: ^21000' % (client.cid))
                self.console.write('tell %s ^7Valor:^2HK^7 / Arma:^2HK69 40mm^7 / Costo: ^22000' % (client.cid))
                self.console.write('tell %s ^7Valor:^2G36^7 / Arma:^2HK G36^7 / Costo: ^21000' % (client.cid))
                self.console.write('tell %s ^7Valor:^2AK^7 / Arma:^2AK103 7.62mm^7 / Costo: ^2700' % (client.cid))
                self.console.write('tell %s ^7Valor:^2NE^7 / Arma:^2IMI Negev^7 / Costo: ^2750' % (client.cid))
                self.console.write('tell %s ^7Valor:^2M4^7 / Arma:^2Colt M4A1^7 / Costo: ^2650' % (client.cid))
                self.console.write('tell %s ^7Valor:^2INV^7 / ^2Invisible^7 / Costo: ^2150000' % (client.cid))
                self.console.write('tell %s ^7Valor:^2GOD^7 / ^2Godmode^7 / Costo: ^230000' % (client.cid))
                self.console.write('tell %s ^7Valor:^2KL^7 / ^2Kill^7 / Costo: ^210000' % (client.cid))
                self.console.write('tell %s ^7Valor:^2TP^7 / ^2Teleport^7 / Equipo: ^21000 ^7Enemigo: ^25000' % (client.cid))
                return True
            elif(idioma == "FR"):
                self.console.write('tell %s In French: ^7Key:^2SR8^7 / Weapon:^2Remington SR8^7 / Price: ^2600' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2SPAS^7 / Weapon:^2Franchi SPAS12^7 / Price: ^2300' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2MP5^7 / Weapon:^2HK MP5K^7 / Price: ^2500' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2UMP^7 / Weapon:^2UMP45^7 / Price: ^2550' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2LR^7 / Weapon:^2ZM LR300^7 / Price: ^2650' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2PSG^7 / Weapon:^2HK PSG1^7 / Price: ^21000' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2HK^7 / Weapon:^2HK69 40mm^7 / Price: ^22000' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2G36^7 / Weapon:^2HK G36^7 / Price: ^21000' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2AK^7 / Weapon:^2AK103 7.62mm^7 / Price: ^2700' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2NE^7 / Weapon:^2IMI Negev^7 / Price: ^2750' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2M4^7 / Weapon:^2Colt M4A1^7 / Price: ^2650' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2INV^7 / ^2Invisible^7 / Price: ^2150000' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2GOD^7 / ^2Godmode^7 / Price: ^230000' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2KL^7 / ^2Kill^7 / Price: ^210000' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2TP^7 / ^2Teleport^7 / Team: ^21000 ^7Enemy: ^25000' % (client.cid))
                return True
            elif(idioma == "DE"):
                self.console.write('tell %s ^7Key:^2SR8^7 / Waffe:^2Remington SR8^7 / Preis: ^2600' % (client.cid))
                self.console.write('tell %s ^7Key:^2SPAS^7 / Waffe:^2Franchi SPAS12^7 / Preis: ^2300' % (client.cid))
                self.console.write('tell %s ^7Key:^2MP5^7 / Waffe:^2HK MP5K^7 / Preis: ^2500' % (client.cid))
                self.console.write('tell %s ^7Key:^2UMP^7 / Waffe:^2UMP45^7 / Preis: ^2550' % (client.cid))
                self.console.write('tell %s ^7Key:^2LR^7 / Waffe:^2ZM LR300^7 / Preis: ^2650' % (client.cid))
                self.console.write('tell %s ^7Key:^2PSG^7 / Waffe:^2HK PSG1^7 / Preis: ^21000' % (client.cid))
                self.console.write('tell %s ^7Key:^2HK^7 / Waffe:^2HK69 40mm^7 / Preis: ^22000' % (client.cid))
                self.console.write('tell %s ^7Key:^2G36^7 / Waffe:^2HK G36^7 / Preis: ^21000' % (client.cid))
                self.console.write('tell %s ^7Key:^2AK^7 / Waffe:^2AK103 7.62mm^7 / Preis: ^2700' % (client.cid))
                self.console.write('tell %s ^7Key:^2NE^7 / Waffe:^2IMI Negev^7 / Preis: ^2750' % (client.cid))
                self.console.write('tell %s ^7Key:^2M4^7 / Waffe:^2Colt M4A1^7 / Preis: ^2650' % (client.cid))
                self.console.write('tell %s ^7Key:^2INV^7 / ^2Unsichtbarkeit^7 / Preis: ^2150000' % (client.cid))
                self.console.write('tell %s ^7Key:^2GOD^7 / ^2Godmode^7 / Preis: ^230000' % (client.cid))
                self.console.write('tell %s ^7Key:^2KL^7 / ^2Kill^7 / Preis: ^210000' % (client.cid))
                self.console.write('tell %s ^7Key:^2TP^7 / ^2Teleport^7 / Team: ^21000 ^7Enemy: ^25000' % (client.cid))
                return True
            elif(idioma == "IT"):
                self.console.write('tell %s ^7Digita:^2SR8^7 / Weapon:^2Remington SR8^7 / Prezzo: ^2600' % (client.cid))
                self.console.write('tell %s ^7Digita:^2SPAS^7 / Weapon:^2Franchi SPAS12^7 / Prezzo: ^2300' % (client.cid))
                self.console.write('tell %s ^7Digita:^2MP5^7 / Weapon:^2HK MP5K^7 / Prezzo: ^2500' % (client.cid))
                self.console.write('tell %s ^7Digita:^2UMP^7 / Weapon:^2UMP45^7 / Prezzo: ^2550' % (client.cid))
                self.console.write('tell %s ^7Digita:^2LR^7 / Weapon:^2ZM LR300^7 / Prezzo: ^2650' % (client.cid))
                self.console.write('tell %s ^7Digita:^2PSG^7 / Weapon:^2HK PSG1^7 / Prezzo: ^21000' % (client.cid))
                self.console.write('tell %s ^7Digita:^2HK^7 / Weapon:^2HK69 40mm^7 / Prezzo: ^22000' % (client.cid))
                self.console.write('tell %s ^7Digita:^2G36^7 / Weapon:^2HK G36^7 / Prezzo: ^21000' % (client.cid))
                self.console.write('tell %s ^7Digita:^2AK^7 / Weapon:^2AK103 7.62mm^7 / Prezzo: ^2700' % (client.cid))
                self.console.write('tell %s ^7Digita:^2NE^7 / Weapon:^2IMI Negev^7 / Prezzo: ^2750' % (client.cid))
                self.console.write('tell %s ^7Digita:^2M4^7 / Weapon:^2Colt M4A1^7 / Prezzo: ^2650' % (client.cid))
                self.console.write('tell %s ^7Digita:^2INV^7 / ^2Invisible^7 / Prezzo: ^2150000' % (client.cid))
                self.console.write('tell %s ^7Digita:^2GOD^7 / ^2Godmode^7 / Prezzo: ^230000' % (client.cid))
                self.console.write('tell %s ^7Digita:^2KL^7 / ^2Kill^7 / Prezzo: ^210000' % (client.cid))
                self.console.write('tell %s ^7Digita:^2TP^7 / ^2Teleport^7 / Team: ^21000 ^7Nemico: ^25000' % (client.cid))
                return True
        if client.team == b3.TEAM_RED:
            if(idioma == "EN"):
                self.console.write('tell %s ^7Key:^2HE^7 / Weapon:^2HE Grenade^7 / Price:^2 350' % (client.cid))
                self.console.write('tell %s ^7Key:^2SM^7 / Weapon:^2SMOKE Grenade^7 / Price:^2 250' % (client.cid))
                self.console.write('tell %s ^7Key:^2KN^7 / Weapon:^2Knife^7 / Price:^2 300' % (client.cid))
                self.console.write('tell %s ^7Key:^2KEV^7 / Weapon:^2Kevlar Vest^7 / Price:^2 1200' % (client.cid))
                self.console.write('tell %s ^7Key:^2HEL^7 / Weapon:^2Helmet^7 / Price:^2 800' % (client.cid))
                self.console.write('tell %s ^7Key:^2MED^7 / Weapon:^2Medkit^7 / Price:^2 500' % (client.cid))
                self.console.write('tell %s ^7Key:^2NVG^7 / Weapon:^2TacGoggles^7 / Price:^2 200' % (client.cid))
                self.console.write('tell %s ^7Key:^2HEAL^7 / Weapon:^2Health^7 / Price:^2 2000' % (client.cid))
                self.console.write('tell %s ^7Key:^2KL^7 / ^2Kill^7 / Price: ^210000' % (client.cid))
                self.console.write('tell %s ^7Key:^2DIS^7 / ^2Disarm^7 / Price: ^23000' % (client.cid))
                self.console.write('tell %s ^7Key:^2TP^7 / ^2Teleport^7 / Team: ^21000 ^7Enemy: ^25000' % (client.cid))
                return True
            elif(idioma == "ES"):
                self.console.write('tell %s ^7Valor:^2HE^7 / Arma:^2HE Grenade^7 / Costo:^2 350' % (client.cid))
                self.console.write('tell %s ^7Valor:^2SM^7 / Arma:^2SMOKE Grenade^7 / Costo:^2 250' % (client.cid))
                self.console.write('tell %s ^7Valor:^2KN^7 / Arma:^2Knife^7 / Costo:^2 300' % (client.cid))
                self.console.write('tell %s ^7Valor:^2KEV^7 / Arma:^2Kevlar Vest^7 / Costo:^2 1200' % (client.cid))
                self.console.write('tell %s ^7Valor:^2HEL^7 / Arma:^2Helmet^7 / Costo:^2 800' % (client.cid))
                self.console.write('tell %s ^7Valor:^2MED^7 / Arma:^2Medkit^7 / Costo:^2 500' % (client.cid))
                self.console.write('tell %s ^7Valor:^2NVG^7 / Arma:^2TacGoggles^7 / Costo:^2 200' % (client.cid))
                self.console.write('tell %s ^7Valor:^2HEAL^7 / Arma:^2Health^7 / Costo:^2 2000' % (client.cid))
                self.console.write('tell %s ^7Valor:^2KL^7 / ^2Kill^7 / Costo: ^210000' % (client.cid))
                self.console.write('tell %s ^7Valor:^2DIS^7 / ^2Disarm^7 / Costo: ^23000' % (client.cid))
                self.console.write('tell %s ^7Valor:^2TP^7 / ^2Teleport^7 / Equipo: ^21000 ^7Enemigo: ^25000' % (client.cid))
                return True
            elif(idioma == "FR"):
                self.console.write('tell %s In French: ^7Key:^2HE^7 / Weapon:^2HE Grenade^7 / Price:^2 350' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2SM^7 / Weapon:^2SMOKE Grenade^7 / Price:^2 250' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2KN^7 / Weapon:^2Knife^7 / Price:^2 300' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2KEV^7 / Weapon:^2Kevlar Vest^7 / Price:^2 1200' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2HEL^7 / Weapon:^2Helmet^7 / Price:^2 800' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2MED^7 / Weapon:^2Medkit^7 / Price:^2 500' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2NVG^7 / Weapon:^2TacGoggles^7 / Price:^2 200' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2HEAL^7 / Weapon:^2Health^7 / Price:^2 2000' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2KL^7 / ^2Kill^7 / Price: ^210000' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2DIS^7 / ^2Disarm^7 / Price: ^23000' % (client.cid))
                self.console.write('tell %s In French: ^7Key:^2TP^7 / ^2Teleport^7 / Team: ^21000 ^7Enemy: ^25000' % (client.cid))
                return True
            elif(idioma == "DE"):
                self.console.write('tell %s ^7Key:^2HE^7 / Waffe:^2HE Grenade^7 / Preis:^2 350' % (client.cid))
                self.console.write('tell %s ^7Key:^2SM^7 / Waffe:^2SMOKE Grenade^7 / Preis:^2 250' % (client.cid))
                self.console.write('tell %s ^7Key:^2KN^7 / Waffe:^2Knife^7 / Preis:^2 300' % (client.cid))
                self.console.write('tell %s ^7Key:^2KEV^7 / Waffe:^2Kevlar Vest^7 / Preis:^2 1200' % (client.cid))
                self.console.write('tell %s ^7Key:^2HEL^7 / Waffe:^2Helmet^7 / Preis:^2 800' % (client.cid))
                self.console.write('tell %s ^7Key:^2MED^7 / Waffe:^2Medkit^7 / Preis:^2 500' % (client.cid))
                self.console.write('tell %s ^7Key:^2NVG^7 / Waffe:^2TacGoggles^7 / Preis:^2 200' % (client.cid))
                self.console.write('tell %s ^7Key:^2HEAL^7 / Waffe:^2Health^7 / Preis:^2 2000' % (client.cid))
                self.console.write('tell %s ^7Key:^2KL^7 / ^2Kill^7 / Preis: ^210000' % (client.cid))
                self.console.write('tell %s ^7Key:^2DIS^7 / ^Entwaffnen^7 / Preis: ^23000' % (client.cid))
                self.console.write('tell %s ^7Key:^2TP^7 / ^2Teleport^7 / Team: ^21000 ^7Enemy: ^25000' % (client.cid))
                return True
            elif(idioma == "IT"):
                self.console.write('tell %s ^7Digita:^2HE^7 / Weapon:^2HE Grenade^7 / Prezzo:^2 350' % (client.cid))
                self.console.write('tell %s ^7Digita:^2SM^7 / Weapon:^2SMOKE Grenade^7 / Prezzo:^2 250' % (client.cid))
                self.console.write('tell %s ^7Digita:^2KN^7 / Weapon:^2Knife^7 / Prezzo:^2 300' % (client.cid))
                self.console.write('tell %s ^7Digita:^2KEV^7 / Weapon:^2Kevlar Vest^7 / Prezzo:^2 1200' % (client.cid))
                self.console.write('tell %s ^7Digita:^2HEL^7 / Weapon:^2Helmet^7 / Prezzo:^2 800' % (client.cid))
                self.console.write('tell %s ^7Digita:^2MED^7 / Weapon:^2Medkit^7 / Prezzo:^2 500' % (client.cid))
                self.console.write('tell %s ^7Digita:^2NVG^7 / Weapon:^2TacGoggles^7 / Prezzo:^2 200' % (client.cid))
                self.console.write('tell %s ^7Digita:^2HEAL^7 / Weapon:^2Health^7 / Prezzo:^2 2000' % (client.cid))
                self.console.write('tell %s ^7Digita:^2KL^7 / ^2Kill^7 / Prezzo: ^210000' % (client.cid))
                self.console.write('tell %s ^7Digita:^2DIS^7 / ^2Disarm^7 / Prezzo: ^23000' % (client.cid))
                self.console.write('tell %s ^7Digita:^2TP^7 / ^2Teleport^7 / Team: ^21000 ^7Nemico: ^25000' % (client.cid))
                return True
                    
    def putOnOff(self, client, status, key, valor, weapon, nombre):
        q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
        self.debug(q)
        cursor = self.console.storage.query(q)
        r = cursor.getRow()
        idioma = r['idioma']
        azul = r['azul']
        rojo = r['rojo']
        if(status == "on") or (status == "ON"):
            if client.team == b3.TEAM_BLUE:
                if ("%s" % key) not in azul:
                    lol = azul.replace(azul, azul+("%s" % key));
                    q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul+%s WHERE iduser = "%s"' % (lol,valor,client.id))
                    self.console.storage.query(q)
                    self.autoBuying(client, idioma, weapon)
                else:
                    self.autoBuyingAlready(client, idioma, weapon)
            elif client.team == b3.TEAM_RED:
                if ("%s" % key) not in rojo:
                    lol = rojo.replace(rojo, rojo+("%s" % key));
                    q=('UPDATE `dinero` SET `rojo`="%s",`precio_rojo`=precio_rojo+%s WHERE iduser = "%s"' % (lol,valor,client.id))
                    self.console.storage.query(q)
                    self.autoBuying(client, idioma, weapon)
                else:
                    self.autoBuyingAlready(client, idioma, weapon)
        elif(status == "off") or (status == "OFF"):
            if client.team == b3.TEAM_BLUE:
                if ("%s" % key) in azul:
                    lol = azul.replace(("%s" % key),"");
                    q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul-%s WHERE iduser = "%s"' % (lol, valor, client.id))
                    self.console.storage.query(q)
                    self.autoBuyingStop(client, idioma, weapon)
                else:
                    self.autoBuyingNot(client, idioma)
            elif client.team == b3.TEAM_RED:
                if ("%s" % key) in rojo:
                    lol = rojo.replace(("%s" % key),"");
                    q=('UPDATE `dinero` SET `rojo`="%s",`precio_rojo`=precio_rojo-%s WHERE iduser = "%s"' % (lol, valor, client.id))
                    self.console.storage.query(q)
                    self.autoBuyingStop(client, idioma, weapon)
                else:
                    self.autoBuyingNot(client, idioma)
                    
    def buyItem(self, client, key, valor, nombre):
        q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
        self.debug(q)
        cursor = self.console.storage.query(q)
        r = cursor.getRow()
        dinero = r['dinero']
        idioma = r['idioma']
        if(client.maxLevel >= 100):
            self.console.write("gi %s %s" % (client.cid, key))
            return True
        else:
            if (valor > dinero):
                self.noCoins(client, idioma, dinero)
            else:
                q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
                self.console.storage.query(q)
                self.console.write("gi %s %s" % (client.cid, key))
                sobran = (dinero - valor)
                self.clientBought(client, idioma, nombre, sobran)
                
    def buyWeapon(self, client, key, valor, nombre):
        q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
        self.debug(q)
        cursor = self.console.storage.query(q)
        r = cursor.getRow()
        dinero = r['dinero']
        idioma = r['idioma']
        if(client.maxLevel >= 100):
            self.console.write("gw %s %s" % (client.cid, key))
            return True
        else:
            if (valor > dinero):
                self.noCoins(client, idioma, dinero)
            else:
                q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
                self.console.storage.query(q)
                self.console.write("gw %s %s" % (client.cid, key))
                sobran = (dinero - valor)
                self.clientBought(client, idioma, nombre, sobran)
                
    def buyVeces(self, client, key, valor, nombre, veces):
        q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
        self.debug(q)
        cursor = self.console.storage.query(q)
        r = cursor.getRow()
        dinero = r['dinero']
        idioma = r['idioma']
        valorTotal = (valor * veces)
            
        if (valorTotal > dinero):
            self.noCoins(client, idioma, dinero)
        else:
            q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valorTotal, client.id))
            self.console.storage.query(q)
            sobran = (dinero - valorTotal)
            self.console.write("gw %s %s +%s" % (client.cid, key, veces))
            if(idioma == "EN"):
                client.message("You have Bought ^5%s ^2%s ^7You have:^2%s ^7Coins" % (veces, nombre, sobran))
            elif(idioma == "ES"):
                client.message('^7Has Comprado ^5%s ^2%s ^7Te Quedan: ^2%s ^7Coins' % (veces, nombre, sobran))
            elif(idioma == "FR"):
                client.message("In French: You have Bought ^5%s ^2%s ^7You have:^2%s ^7Coins" % (veces, nombre, sobran))
            elif(idioma == "DE"):
                client.message("Du hast ^5%s und ^2%s ^7gekauft.Du hast noch: ^2%s ^7Coins" % (veces, nombre, sobran))
            elif(idioma == "IT"):
                client.message('Hai comprato ^5%s ^2%s ^7Hai:^2%s ^7coins' % (veces, nombre, sobran))
            
    def stopInv(self, client):
        Status = self.get_spree_stats(client)
        Status.inv = False
        client.message('Your ^4Invisible ^7time finishes in ^53')
        time.sleep(2)
        client.message('Your ^4Invisible ^7time finishes in ^52')
        time.sleep(2)
        client.message('Your ^4Invisible ^7time finishes in ^51')
        time.sleep(2)
        
        self.console.write('forcecvar %s cg_rgb "1"' % (client.cid))
        self.console.write('forcecvar %s cg_rgb "0"' % (client.cid))
        self.console.write('bigtext "%s ^7is now ^2Visible ^7again!"' % (client.exactName))
            
    def cmd_getweapon(self, data, client=None, cmd=None):
        """\
        ^6Type ^2!buy help / !buy ayuda
        """
        q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
        self.debug(q)
        cursor = self.console.storage.query(q)
        r = cursor.getRow()
        dinero = r['dinero']
        idioma = r['idioma']
        input = self._adminPlugin.parseUserCmd(data)
        if not data:
            if(idioma == "EN"):
                client.message('Type ^2!buy help ^7to see how to use this command')
            elif(idioma == "ES"):
                client.message('Escribe ^2!buy ayuda ^7para ver como usar este comando')
            elif(idioma == "FR"):
                client.message("In French: Type ^2!buy help ^7to see how to use this command")
            elif(idioma == "DE"):
                client.message("Schreibe ^2!buy help ^7um den Gebrauch dieses Kommandos zu erfahren")
            elif(idioma == "IT"):
                client.message("Scrivi ^2!buy help ^7per vedere come utilizzare questo comando")
            return False
        weapon = input[0]
        status = input[1]
        veces = input[1]
        if(weapon == "help") or (weapon == "ayuda") or (weapon == "In French: help")or (weapon == "In German: help"):
            if(idioma == "EN"):
                self.console.write('tell %s ^7Type ^2!money ^7to see your money' % (client.cid))
                self.console.write('tell %s ^7Type ^2!bl ^7to see the weapons and items prices' % (client.cid))
                self.console.write('tell %s ^7Type ^2!b ^4<weapon or item> ^7to buy whatever you want' % (client.cid))
                self.console.write('tell %s ^7Type ^2!price <weapon, item or command> ^7to see a concrete price' % (client.cid))
                self.console.write('tell %s ^7Type ^2!pay ^4<player> <amount> ^7to give money to a player' % (client.cid))
                self.console.write('tell %s ^7Type ^2!disarm ^4<player> ^7to disarm a human enemy' % (client.cid))
                self.console.write('tell %s ^7Type ^2!moneytopstats ^7to see money top players' % (client.cid))
                self.console.write('tell %s ^7Type ^2!tp ^4<player> ^7to teleport to a player' % (client.cid))
                self.console.write('tell %s ^7Type ^2!kill ^4<player> ^7to kill a enemy' % (client.cid))
                self.console.write('tell %s ^7Type ^2!b god ^7to buy godmode(for one round)' % (client.cid))
                self.console.write('tell %s ^7Type ^2!b inv ^7to buy invisible(until teams swap)' % (client.cid))
            elif(idioma == "ES"):
                self.console.write('tell %s ^7Escribe ^2!money ^7para ver tu dinero' % (client.cid))
                self.console.write('tell %s ^7Escribe ^2!bl ^7para ver la lista de armas y precios' % (client.cid))
                self.console.write('tell %s ^7Escribe ^2!b ^4<arma or item> ^7para comprar el arma que quieras' % (client.cid))
                self.console.write('tell %s ^7Escribe ^2!price <arma, item o comando> ^7para ver un precio concreto' % (client.cid))
                self.console.write('tell %s ^7Escribe ^2!pay ^4<jugador> <cantidad> ^7para dar dinero a un jugador' % (client.cid))
                self.console.write('tell %s ^7Escribe ^2!disarm ^4<player> ^7para desarmar a un enemigo humano' % (client.cid))
                self.console.write('tell %s ^7Escribe ^2!tp ^4<player> ^7para teletransportarte a un jugador' % (client.cid))
                self.console.write('tell %s ^7Escribe ^2!kill ^4<player> ^7para matar a un jugador' % (client.cid))
                self.console.write('tell %s ^7Escribe ^2!b god ^7para comprar godmode(durante una ronda)' % (client.cid))
                self.console.write('tell %s ^7Escribe ^2!b inv ^7para comprar invisible(hasta el cambio de equipos)' % (client.cid))
            elif(idioma == "FR"):
                self.console.write('tell %s In French: ^7Type ^2!money ^7to see your money' % (client.cid))
                self.console.write('tell %s In French: ^7Type ^2!bl ^7to see the weapons and items prices' % (client.cid))
                self.console.write('tell %s In French: ^7Type ^2!b ^4<weapon or item> ^7to buy whatever you want' % (client.cid))
                self.console.write('tell %s In French: ^7Type ^2!price <weapon, item or command> ^7to see a concrete price' % (client.cid))
                self.console.write('tell %s In French: ^7Type ^2!pay ^4<player> <amount> ^7to give money to a player' % (client.cid))
                self.console.write('tell %s In French: ^7Type ^2!disarm ^4<player> ^7to disarm a human enemy' % (client.cid))
                self.console.write('tell %s In French: ^7Type ^2!moneytopstats ^7to see money top players' % (client.cid))
                self.console.write('tell %s In French: ^7Type ^2!tp ^4<player> ^7to teleport to a player' % (client.cid))
                self.console.write('tell %s In French: ^7Type ^2!kill ^4<player> ^7to kill a enemy' % (client.cid))
                self.console.write('tell %s In French: ^7Type ^2!b god ^7to buy godmode(for one round)' % (client.cid))
                self.console.write('tell %s In French: ^7Type ^2!b inv ^7to buy invisible(until teams swap)' % (client.cid))
            elif(idioma == "DE"):
                self.console.write('tell %s ^7Schreibe ^2!money ^7um die Menge deiner Coins zu sehen' % (client.cid))
                self.console.write('tell %s ^7Schreibe ^2!bl ^7um die Preise der Waffen und Items zu sehen' % (client.cid))
                self.console.write('tell %s ^7Schreibe ^2!b ^4<weapon oder item> ^7um etwas zu kaufen' % (client.cid))
                self.console.write('tell %s ^7Schreibe ^2!price <weapon, item oder command> ^7um einen einzelnen Preis zu sehen' % (client.cid))
                self.console.write('tell %s ^7Schreibe ^2!pay ^4<player> <amount> ^7um einem Spieler Coins zu geben' % (client.cid))
                self.console.write('tell %s ^7Schreibe ^2!disarm ^4<player> ^7um einen Human-Spieler zu entwaffnen' % (client.cid))
                self.console.write('tell %s ^7Schreibe ^2!moneytopstats ^7um die Ersten in der Coin-Rangliste zu sehen' % (client.cid))
                self.console.write('tell %s ^7Schreibe ^2!tp ^4<player> ^7um dich zu einem Spieler zu teleportieren' % (client.cid))
                self.console.write('tell %s ^7Schreibe ^2!kill ^4<player> ^7um einen Spieler zu toeten' % (client.cid))
                self.console.write('tell %s ^7Schreibe ^2!b god ^7um den GODMODE fuer eine Runde zu aktivieren' % (client.cid))
                self.console.write('tell %s ^7Schreibe ^2!b inv ^7um Unsichtbarkeit zu kaufen (bis die Teams tauschen)' % (client.cid))
            elif(idioma == "IT"):
                self.console.write('tell %s ^7Scrivi ^2!money ^7per sapere quanti coins hai' % (client.cid))
                self.console.write('tell %s ^7Scrivi ^2!bl ^7per vedere i prezzi delle armi e degli oggetti' % (client.cid))
                self.console.write('tell %s ^7Scrivi ^2!b ^4<weapon or item> ^7per comprare quello che vuoi' % (client.cid))
                self.console.write('tell %s ^7Scrivi ^2!price <weapon, item or command> ^7per vedere un singolo prezzo' % (client.cid))
                self.console.write('tell %s ^7Scrivi ^2!pay ^4<player> <amount> ^7per dare coins a un giocatore' % (client.cid))
                self.console.write('tell %s ^7Scrivi ^2!disarm ^4<player> ^7per disarmare un nemico' % (client.cid))
                self.console.write('tell %s ^7Scrivi ^2!moneytopstats ^7per vedere i money top players' % (client.cid))
                self.console.write('tell %s ^7Scrivi ^2!tp ^4<player> ^7per teletrasportarti a un giocatore' % (client.cid))
                self.console.write('tell %s ^7Scrivi ^2!kill ^4<player> ^7per uccidere un nemico' % (client.cid))
                self.console.write('tell %s ^7Scrivi ^2!b god ^7per acquistare godmode(per un turno)' % (client.cid))
                self.console.write('tell %s ^7Scrivi ^2!b inv ^7per diventare invisibile(fino a che i team non vengono invertiti)' % (client.cid))
            return False
        if client.team == b3.TEAM_BLUE:
            if (weapon == "god") or (weapon == "godmode"):
                nombre = god.nombre
                valor = god.valor
                if(client.maxLevel >= 100):
                    self.console.write("exec god%s.cfg" % (client.cid))
                    self.console.write('bigtext "%s ^7Is ^6GoD"' % (client.exactName))
                    return True
                else:
                    if veces:
                        regex = re.compile(r"""^(?P<string>\w+) (?P<number>\d+)$""")
                        match = regex.match(data)
                        weapon = match.group('string')
                        veces = int(match.group('number'))
                        if veces <= 0:
                          client.message('You cant buy ^5%s ^7rounds!' % (veces))
                          return False
                        valor = (valor * veces)
                    else:
                        veces = 0
                    q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
                    cursor = self.console.storage.query(q)
                    r = cursor.getRow()
                    dinero = r['dinero']
                    idioma = r['idioma']
                    if(dinero > valor):
                        q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor, client.id))
                        self.console.storage.query(q)
                        self.console.write("exec god%s.cfg" % (client.cid))
                        self.console.write('bigtext "%s ^7bought ^6GoDMoDe ^7for ^5%s ^7Rounds!"' % (client.exactName, veces))
                        Status = self.get_spree_stats(client)
                        Status.god += veces
                        sobran = (dinero - valor)
                        if(idioma == "EN"):
                            client.message('You Have Bought ^6%s ^7for ^5%s ^7Rounds You have: ^2%s ^7Coins' % (nombre, veces, sobran))
                        elif(idioma == "ES"):
                            client.message('Has Comprado ^6%s ^7durante ^5%s ^7Rondas Te Quedan: ^2%s ^7Coins' % (nombre, veces, sobran))
                        elif(idioma == "FR"):
                            client.message("In French: You Have Bought ^6%s ^7for ^5%s^7Rounds You have: ^2%s ^7Coins" % (nombre, veces, sobran))
                        elif(idioma == "DE"):
                            client.message("In German: You Have Bought ^6%s ^7for ^5%s^7Rounds You have: ^2%s ^7Coins" % (nombre, veces, sobran))
                        elif(idioma == "IT"):
                            client.message("In Ita: You Have Bought ^6%s ^7for ^5%s^7Rounds You have: ^2%s ^7Coins" % (nombre, veces, sobran))
                    else:
                        self.noCoins(client, idioma, dinero)
                        
            elif (weapon == "inv") or (weapon == "invisible"):   
                nombre = invisible.nombre
                valor = invisible.valor  
                if(client.maxLevel >= 100):
                    self.console.write("inv %s" % (client.cid))
                    self.console.write('bigtext "%s ^7Is ^4Invisible"' % (client.exactName))
                    return True
                else:
                    if veces:
                        regex = re.compile(r"""^(?P<string>\w+) (?P<number>\d+)$""")
                        match = regex.match(data)
                        weapon = match.group('string')
                        veces = int(match.group('number'))
                        if veces <= 0:
                          client.message('You cant buy ^5%s ^7minutes!' % (veces))
                          return False
                        valor = (valor * veces)
                    else:
                        veces = 1
                    q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
                    cursor = self.console.storage.query(q)
                    r = cursor.getRow()
                    dinero = r['dinero']
                    idioma = r['idioma']
                    if(dinero > valor):
                        q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor, client.id))
                        self.console.storage.query(q)
                        self.console.write("inv %s" % (client.cid))
                        self.console.write('bigtext "%s ^7bought ^4Invisible ^7for ^5%s ^7minutes!"' % (client.exactName, veces))
                        Status = self.get_spree_stats(client)
                        Status.inv = True
                        t = threading.Timer((veces * 60), self.stopInv, args=[client])
                        t.start()
                        sobran = (dinero - valor)
                        if(idioma == "EN"):
                            client.message('You Have Bought ^6%s ^7for ^5%s^7min You have: ^2%s ^7Coins' % (nombre, veces, sobran))
                        elif(idioma == "ES"):
                            client.message('Has Comprado ^6%s ^7por ^5%s^7min Te Quedan: ^2%s ^7Coins' % (nombre, veces, sobran))
                        elif(idioma == "FR"):
                            client.message("In French: You Have Bought ^6%s ^7for ^5%s^7min You have: ^2%s ^7Coins" % (nombre, veces, sobran))
                        elif(idioma == "DE"):
                            client.message("In German: You Have Bought ^6%s ^7for ^5%s^7min You have: ^2%s ^7Coins" % (nombre, veces, sobran))
                        elif(idioma == "IT"):
                            client.message("In Ita: You Have Bought ^6%s ^7for ^5%s^7min You have: ^2%s ^7Coins" % (nombre, veces, sobran))
                    else:
                        self.noCoins(client, idioma, dinero)

            elif (weapon == "sr8") or (weapon == "SR8"):
                nombre = sr8.nombre
                key = sr8.key
                valor = sr8.valor
                
                if status:
                    self.putOnOff(client, status, key, valor, weapon, nombre)
                    return False
                else:
                    self.buyWeapon(client, key, valor, nombre)
                    
            elif (weapon == "spas") or (weapon == "SPAS") or (weapon == "FRANCHI") or (weapon == "franchi"):
                nombre = spas.nombre
                key = spas.key
                valor = spas.valor
                
                if status:
                    self.putOnOff(client, status, key, valor, weapon, nombre)
                    return False
                else:
                    self.buyWeapon(client, key, valor, nombre)
                    
            elif (weapon == "mp5") or (weapon == "MP5") or (weapon == "MP5K") or (weapon == "mp5k"):
                nombre = mp5.nombre
                key = mp5.key
                valor = mp5.valor
                
                if status:
                    self.putOnOff(client, status, key, valor, weapon, nombre)
                    return False
                else:
                    self.buyWeapon(client, key, valor, nombre)

            elif (weapon == "ump") or (weapon == "UMP") or (weapon == "UMP45") or (weapon == "ump45"):
                nombre = ump.nombre
                key = ump.key
                valor = ump.valor
                
                if status:
                    self.putOnOff(client, status, key, valor, weapon, nombre)
                    return False
                else:
                    self.buyWeapon(client, key, valor, nombre)

            elif (weapon == "HK69") or (weapon == "hk69") or (weapon == "hk") or (weapon == "HK"):
                nombre = hk.nombre
                key = hk.key
                valor = hk.valor
                
                if status:
                    self.putOnOff(client, status, key, valor, weapon, nombre)
                    return False
                else:
                    self.buyWeapon(client, key, valor, nombre)
                    
            elif (weapon == "lr300") or (weapon == "LR300") or (weapon == "LR") or (weapon == "lr"):
                nombre = lr.nombre
                key = lr.key
                valor = lr.valor
                
                if status:
                    self.putOnOff(client, status, key, valor, weapon, nombre)
                    return False
                else:
                    self.buyWeapon(client, key, valor, nombre)

            elif (weapon == "PSG") or (weapon == "psg") or (weapon == "PSG1") or (weapon == "psg1"):
                nombre = psg.nombre
                key = psg.key
                valor = psg.valor
                
                if status:
                    self.putOnOff(client, status, key, valor, weapon, nombre)
                    return False
                else:
                    self.buyWeapon(client, key, valor, nombre)
                    
            elif (weapon == "g36") or (weapon == "G36"):
                nombre = g36.nombre
                key = g36.key
                valor = g36.valor
                
                if status:
                    self.putOnOff(client, status, key, valor, weapon, nombre)
                    return False
                else:
                    self.buyWeapon(client, key, valor, nombre)

            elif (weapon == "ak") or (weapon == "AK") or (weapon == "AK103") or (weapon == "ak103"):
                nombre = ak.nombre
                key = ak.key
                valor = ak.valor
                
                if status:
                    self.putOnOff(client, status, key, valor, weapon, nombre)
                    return False
                else:
                    self.buyWeapon(client, key, valor, nombre)

            elif (weapon == "NEGEV") or (weapon == "negev") or (weapon == "NE") or (weapon == "ne"):
                nombre = negev.nombre
                key = negev.key
                valor = negev.valor
                
                if status:
                    self.putOnOff(client, status, key, valor, weapon, nombre)
                    return False
                else:
                    self.buyWeapon(client, key, valor, nombre)
                    
            elif (weapon == "M4") or (weapon == "m4") or (weapon == "m4a") or (weapon == "M4A"):
                nombre = m4.nombre
                key = m4.key
                valor = m4.valor
                
                if status:
                    self.putOnOff(client, status, key, valor, weapon, nombre)
                    return False
                else:
                    self.buyWeapon(client, key, valor, nombre)
            else:
                if(idioma == "ES"):
                    client.message("^7No se encontro: ^1%s^7" % input[0])
                elif(idioma == "IT"):
                    client.message("^7Impossibile trovare: ^1%s^7" % input[0])
                else:
                    client.message("^7Couldn't find: ^1%s^7" % input[0])
            return False
                
        if client.team == b3.TEAM_RED:
            weapon = input[0]
            status = input[1]
            veces = input[1]
                               ############################## HE Grenade ##############################
            if (weapon == "grenade") or (weapon == "GRENADE") or (weapon == "HE") or (weapon == "he"):
                nombre = he.nombre
                key = he.key
                valor = he.valor
                
                if client.maxLevel >= 100:
                    if veces:
                        self.console.write("gw %s %s +%s" % (client.cid, key, veces))
                    else:
                        self.console.write("gw %s %s +1" % (client.cid, key))
                else:
                    if veces:
                        regex = re.compile(r"""^(?P<string>\w+) (?P<number>\d+)$""")
                        match = regex.match(data)
                        weapon = match.group('string')
                        veces = int(match.group('number'))
                        self.buyVeces(client, key, valor, nombre, veces)
                    else:
                        self.buyWeapon(client, key, valor, nombre)
                            
            elif (weapon == "SMOKE") or (weapon == "smoke") or (weapon == "SM") or (weapon == "sm"):
                nombre = smoke.nombre
                key = smoke.key
                valor = smoke.valor
                
                if client.maxLevel >= 100:
                    if veces:
                        self.console.write("gw %s %s +%s" % (client.cid, key, veces))
                    else:
                        self.console.write("gw %s %s +1" % (client.cid, key))
                else:
                    if veces:
                        regex = re.compile(r"""^(?P<string>\w+) (?P<number>\d+)$""")
                        match = regex.match(data)
                        weapon = match.group('string')
                        veces = int(match.group('number'))
                        self.buyVeces(client, key, valor, nombre, veces)
                    else:
                        self.buyWeapon(client, key, valor, nombre)
                        
            elif (weapon == "KNIFE") or (weapon == "knife") or (weapon == "kn") or (weapon == "KN"):
                nombre = knife.nombre
                key = knife.key
                valor = knife.valor
                
                if client.maxLevel >= 100:
                    if veces:
                        self.console.write("gw %s %s +%s" % (client.cid, key, veces))
                    else:
                        self.console.write("gw %s %s +1" % (client.cid, key))
                else:
                    if veces:
                        regex = re.compile(r"""^(?P<string>\w+) (?P<number>\d+)$""")
                        match = regex.match(data)
                        weapon = match.group('string')
                        veces = int(match.group('number'))
                        self.buyVeces(client, key, valor, nombre, veces)
                    else:
                        self.buyWeapon(client, key, valor, nombre)
                        
            elif (weapon == "FLASH") or (weapon == "flash") or (weapon == "fla") or (weapon == "FLA"):
                nombre = flash.nombre
                key = flash.key
                valor = flash.valor
                if(client.maxLevel >= 100):
                    if(veces):
                        self.console.write("gw %s L %s" % (client.cid,veces))
                        return True
                    else:
                        self.console.write("gw %s L" % client.cid)
                        return True
                else:
                    if(idioma == "ES"):
                        client.message('^2Flash nade ^7no esta permitida..')
                    elif(idioma == "IT"):
                        client.message('^2Flash nade ^7non e permessa..')
                    else:
                        client.message('^2Flash nade ^7is not allowed..')
                        
            elif (weapon == "kevlar") or (weapon == "KEVLAR") or (weapon == "KEV") or (weapon == "kev"):
                nombre = kevlar.nombre
                key = kevlar.key
                valor = kevlar.valor
                
                if status:
                    self.putOnOff(client, status, key, valor, weapon, nombre)
                    return False
                else:
                    self.buyItem(client, key, valor, nombre)
                    
            elif (weapon == "helmet") or (weapon == "HELMET") or (weapon == "HEL") or (weapon == "hel"):
                nombre = helmet.nombre
                key = helmet.key
                valor = helmet.valor
                
                if status:
                    self.putOnOff(client, status, key, valor, weapon, nombre)
                    return False
                else:
                    self.buyItem(client, key, valor, nombre)
                    
            elif (weapon == "medkit") or (weapon == "MEDKIT") or (weapon == "MEDIC") or (weapon == "medic") or (weapon == "MED") or (weapon == "med"):
                nombre = medkit.nombre
                key = medkit.key
                valor = medkit.valor
                
                if status:
                    self.putOnOff(client, status, key, valor, weapon, nombre)
                    return False
                else:
                    self.buyItem(client, key, valor, nombre)
                    
            elif (weapon == "TAC") or (weapon == "tac") or (weapon == "nvg") or (weapon == "NVG") or (weapon == "goggles") or (weapon == "TacGoggles") or (weapon == "tacgoggles"):
                nombre = tac.nombre
                key = tac.key
                valor = tac.valor
                
                if status:
                    self.putOnOff(client, status, key, valor, weapon, nombre)
                    return False
                else:
                    self.buyItem(client, key, valor, nombre)
                    
            elif (weapon == "HEALTH") or (weapon == "health") or (weapon == "heal") or (weapon == "HEAL") or (weapon == "H") or (weapon == "h"):
                valor = health.valor
                nombre = health.nombre
                if input[1]:
                    sclient = self._adminPlugin.findClientPrompt(input[1], client)
                    if sclient:
                        if(client.maxLevel >= 100):
                            self.console.write("gh %s +100" % sclient.cid)
                            return True
                        else:
                            if (valor > dinero):
                                self.noCoins(client, idioma, dinero)
                            else:
                                q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
                                self.console.storage.query(q)
                                self.console.write("gh %s +100" % sclient.cid)
                                sobran=dinero-valor
                                if(idioma == "ES"):
                                    client.message('^7Has Comprado ^2%s ^7a %s. Te Quedan:^2%s ^7coins' % (nombre,sclient.exactName,sobran))
                                elif(idioma == "IT"):
                                    client.message('^7Hai comprato ^2%s ^7a %s. Hai:^2%s ^7coins' % (nombre,sclient.exactName,sobran))
                                else:
                                    client.message('^7You have Bought ^2%s^7 to %s. You have:^2%s ^7coins' % (nombre,sclient.exactName,sobran))
                                return True
                else:
                    if(client.maxLevel >= 100):
                        self.console.write("gh %s +100" % client.cid)
                        return True
                    else:
                        if (valor > dinero):
                            self.noCoins(client, idioma, dinero)
                        else:
                            q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor, client.id))
                            self.console.storage.query(q)
                            self.console.write("gh %s +100" % client.cid)
                            sobran=dinero-valor
                            self.clientBought(client, idioma, nombre, sobran)
            else:
                if(idioma == "EN"):
                    client.message("Couldn't find: ^1%s" % input[0])
                elif(idioma == "ES"):
                    client.message("No se encontro: ^1%s" % input[0])
                elif(idioma == "FR"):
                    client.message("In French: Couldn't find: ^1%s" % input[0])
                elif(idioma == "DE"):
                    client.message("Konnte ^1%s ^7nicht finden" % input[0])
                elif(idioma == "IT"):
                    client.message("Impossibile trovare: ^1%s" % input[0])
                return False
                
    def autoMessage(self, event):
        for c in self.console.clients.getList():
            if(c.team == b3.TEAM_BLUE):
                q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (c.id))
                cursor = self.console.storage.query(q)
                r = cursor.getRow()
                azul = r['azul']
                dinero = r['dinero']
                precio_azul = r['precio_azul']
                idioma = r['idioma']
                if(c.maxLevel >= 100):
                    self.console.write("gw %s %s" % (c.cid,azul))
                else:
                    if azul:
                        weapon = []
                        if 'N' in azul:
                            weapon.insert( 1, sr8.nombre)
                        if 'D' in azul:
                            weapon.insert( 1, spas.nombre)
                        if 'E' in azul:
                            weapon.insert( 1, mp5.nombre)
                        if 'F' in azul:
                            weapon.insert( 1, ump.nombre)
                        if 'G' in azul:
                            weapon.insert( 1, hk.nombre)
                        if 'H' in azul:
                            weapon.insert( 1, lr.nombre)
                        if 'I' in azul:
                            weapon.insert( 1, g36.nombre)
                        if 'J' in azul:
                            weapon.insert( 1, psg.nombre)
                        if 'O' in azul:
                            weapon.insert( 1, ak.nombre)
                        if 'Q' in azul:
                            weapon.insert( 1, negev.nombre)
                        if 'S' in azul:
                            weapon.insert( 1, m4.nombre)
                        if(dinero > precio_azul):
                            q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (precio_azul,c.id))
                            self.console.storage.query(q)
                            self.console.write("gw %s %s" % (c.cid,azul))
                            c.message('You are autobuying: ^2%s' % ('^7, ^2'.join(weapon)))
                        else:
                            self.noCoins(c, idioma, dinero)
                            
                Status = self.get_spree_stats(c)
                if Status.god > 0:
                    self.console.write("exec god%s.cfg" % (c.cid))
                    Status.god -= 1
                    c.message('^5%s ^7Rounds left to lose your ^6GoD ^7status!' % Status.god)
                if Status.inv == True:
                    self.console.write("inv %s" % (c.cid))
                    
            if(c.team == b3.TEAM_RED):
                q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (c.id))
                cursor = self.console.storage.query(q)
                r = cursor.getRow()
                rojo = r['rojo']
                dinero = r['dinero']
                precio_rojo = r['precio_rojo']
                idioma = r['idioma']
                if(c.maxLevel >= 100):
                    self.console.write("gi %s %s" % (c.cid,rojo))
                else:
                    if rojo:
                        weapon = []
                        if 'K' in rojo:
                            weapon.insert( 1, he.nombre)
                        if 'L' in rojo:
                            weapon.insert( 1, flash.nombre)
                        if 'M' in rojo:
                            weapon.insert( 1, smoke.nombre)
                        if 'A' in rojo:
                            weapon.insert( 1, kevlar.nombre)
                        if 'B' in rojo:
                            weapon.insert( 1, tac.nombre)
                        if 'C' in rojo:
                            weapon.insert( 1, medkit.nombre)
                        if 'F' in rojo:
                            weapon.insert( 1, helmet.nombre)
                        if(dinero > precio_rojo):
                            q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (precio_rojo,c.id))
                            self.console.storage.query(q)
                            self.console.write("gi %s %s" % (c.cid,rojo))
                            c.message('You are autobuying: ^2%s' % ('^7, ^2'.join(weapon)))
                        else:
                            self.noCoins(c, idioma, dinero)
                            
    def clientBought(self, client, idioma, nombre, sobran):
        if(idioma == "EN"):
            client.message('You Have Bought ^2%s ^7You have: ^2%s ^7Coins' % (nombre,sobran))
        elif(idioma == "ES"):
            client.message('Has Comprado ^2%s ^7Te Quedan: ^2%s ^7Coins' % (nombre,sobran))
        elif(idioma == "FR"):
            client.message("In French: You Have Bought ^2%s ^7You have: ^2%s ^7Coins" % (nombre,sobran))
        elif(idioma == "DE"):
            client.message("Du hast ^2%s ^7gekauft. Du hast noch: ^2%s ^7Coins" % (nombre,sobran))
        elif(idioma == "IT"):
            client.message('Hai Comprato ^2%s ^7Hai: ^2%s ^7Coins' % (nombre,sobran))
                            
    def noCoins(self, client, idioma, dinero):
        if(idioma == "EN"):
            client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
        elif(idioma == "ES"):
            client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
        elif(idioma == "FR"):
            client.message("Tu ^1n'as pas ^7assez d'argent. Tu as: ^2%s ^7Coins" % dinero)
        elif(idioma == "DE"):
            client.message("Du hast ^1nicht ^7genug Coins. Du hast: ^2%s ^7Coins" % dinero)
        elif(idioma == "IT"):
            client.message("Non hai ^7abbastanza coins. Hai: ^2%s ^7Coins" % dinero)
    
    def autoBuying(self, client, idioma, weapon):
        if(idioma == "EN"):
            client.message('You ^2started^7 to autobuy ^2%s' % weapon)
        elif(idioma == "ES"):
            client.message('Has ^2comenzado ^7a autocomprar ^2%s' % weapon)
        elif(idioma == "FR"):
            client.message("In French: You ^2started ^7to autobuy ^2%s" % weapon)
        elif(idioma == "DE"):
            client.message("Du ^2aktiviertest ^7autobuy ^2%s" % weapon)
        elif(idioma == "IT"):
            client.message("In Ita: You ^2started ^7to autobuy ^2%s" % weapon)
    
    def autoBuyingStop(self, client, idioma, weapon):
        if(idioma == "EN"):
            client.message('You ^1stopped ^7to autobuy ^2%s' % weapon)
        elif(idioma == "ES"):
            client.message('Has ^1dejado ^7de ^7autocomprar ^2%s' % weapon)
        elif(idioma == "FR"):
            client.message("In French: You ^1stopped ^7to autobuy ^2%s" % weapon)
        elif(idioma == "DE"):
            client.message("Du ^1deaktiviertest ^7autobuy ^2%s" % weapon)
        elif(idioma == "IT"):
            client.message("In Ita: You ^1stopped ^7to autobuy ^2%s" % weapon)
    
    def autoBuyingAlready(self, client, idioma, weapon):
        if(idioma == "EN"):
            client.message('You ^2are already^7 autobuying ^2%s' % weapon)
        elif(idioma == "ES"):
            client.message('^2Ya estas ^7autocomprando ^2%s' % weapon)
        elif(idioma == "FR"):
            client.message("In French: You ^2are already^7 autobuying ^2%s" % weapon)
        elif(idioma == "DE"):
            client.message("Du ^2hast die Waffe schon ^7im autobuy ^2%s" % weapon)
        elif(idioma == "IT"):
            client.message("In Ita: You ^2are already^7 autobuying ^2%s" % weapon)
    
    def autoBuyingNot(self, client, idioma):
        if(idioma == "EN"):
            client.message("You ^1have not^7 activated Autobuy")
        elif(idioma == "ES"):
            client.message("^1No has^7 activado autocomprar")
        elif(idioma == "FR"):
            client.message("In French: You ^1have not^7 activated Autobuy")
        elif(idioma == "DE"):
            client.message("Du hast Autobuy ^1nicht ^7Aktiviert")
        elif(idioma == "IT"):
            client.message('^1Non hai ^7attivato l\'autoacquisto.')
                        
class god():
    nombre = 'GoD'
    valor = 15000
class invisible():
    nombre = 'Invisible'
    valor = 10000
class teleport():
    nombre = 'Teleport'
    price = 1000
class kill():
    nombre = 'Kill'
    price = 10000
class disarm():
    nombre = 'Disarm'
    price = 4000
class sr8():
    nombre = 'Remington SR8'
    key = 'N'
    valor = 600
class spas():
    nombre = 'Franchi SPAS12'
    key = 'D'
    valor = 450
class mp5():
    nombre = 'HK MP5K'
    key = 'E'
    valor = 300
class ump():
    nombre = 'HK UMP45'
    key = 'F'
    valor = 350
class hk():
    nombre = 'HK69 40mm'
    key = 'G'
    valor = 2000
class lr():
    nombre = 'ZM LR300'
    key = 'H'
    valor = 650
class psg():
    nombre = 'HK PSG1'
    key = 'J'
    valor = 1000
class g36():
    nombre = 'HK G36'
    key = 'I'
    valor = 1000
class ak():
    nombre = 'AK103 7.62mm'
    key = 'O'
    valor = 700
class negev():
    nombre = 'IMI Negev'
    key = 'Q'
    valor = 800
class m4():
    nombre = 'Colt M4A1'
    key = 'S'
    valor = 650
class he():
    nombre = 'HE Grenade'
    key = 'K'
    valor = 300
class smoke():
    nombre = 'Smoke Grenade'
    key = 'M'
    valor = 200
class flash():
    nombre = 'Flash Grenade'
    key = 'L'
    valor = 1000
class knife():
    nombre = 'Knife'
    key = 'A'
    valor = 150
class kevlar():
    nombre = 'Kevlar Vest'
    key = 'A'
    valor = 1000
class helmet():
    nombre = 'Helmet'
    key = 'F'
    valor = 800
class medkit():
    nombre = 'Medkit'
    key = 'C'
    valor = 500
class tac():
    nombre = 'TacGoggles'
    key = 'B'
    valor = 2000
class health():
    nombre = 'Health'
    valor = 2000