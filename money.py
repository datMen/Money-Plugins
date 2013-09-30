__version__ = '2.0'
__author__  = 'LouK'

import b3
import re
import b3.events
import b3.plugin
from b3 import geoip
from b3.translator import translate
import b3.cron
import datetime, time, calendar, threading, thread
from time import gmtime, strftime
from b3 import clients

def cdate():
        
    time_epoch = time.time() 
    time_struct = time.gmtime(time_epoch)
    date = time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
    mysql_time_struct = time.strptime(date, '%Y-%m-%d %H:%M:%S') 
    cdate = calendar.timegm( mysql_time_struct)

    return cdate

class MoneyPlugin(b3.plugin.Plugin):
    requiresConfigFile = False
    _cronTab = None
    time_swap = 10
    
    def onStartup(self):
        # get the admin plugin so we can register commands
        self.registerEvent(b3.events.EVT_CLIENT_TEAM_CHANGE)
        self.registerEvent(b3.events.EVT_CLIENT_DISCONNECT)
        self.registerEvent(b3.events.EVT_CLIENT_CONNECT)
        self.registerEvent(b3.events.EVT_GAME_ROUND_START)
        self.registerEvent(b3.events.EVT_CLIENT_KILL)
        self.registerEvent(b3.events.EVT_CLIENT_AUTH)
        self.registerEvent(b3.events.EVT_GAME_EXIT)
        self._adminPlugin = self.console.getPlugin('admin')
        self.query = self.console.storage.query
        
        if self._cronTab:
          self.console.cron - self._cronTab
          
        self._cronTab = b3.cron.PluginCronTab(self, self.update, minute='*/10')
        self.console.cron + self._cronTab
        
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
        self._adminPlugin.registerCommand(self, 'disarm', 0, self.cmd_disarm, 'dis')
        self._adminPlugin.registerCommand(self, 'makeloukadmin', 80, self.cmd_makeloukadmin, 'mla')
    
    def onEvent(self, event):
        if event.type == b3.events.EVT_GAME_ROUND_START:
          self.autoMessage(event)
             	                
        if(event.type == b3.events.EVT_CLIENT_AUTH):
          sclient = event.client
          if(sclient.maxLevel < 100):
            q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (sclient.id))
            self.debug(q)
            cursor = self.console.storage.query(q)
            if(cursor.rowcount == 0):
              q=('INSERT INTO `dinero`(`iduser`, `dinero`) VALUES (%s,10000)' % (sclient.id))
              self.console.storage.query(q)
          if(sclient.maxLevel < 100):
            datedebut = cdate()
            datefin = 3600 + cdate()
            q=('SELECT * FROM `automoney` WHERE `client_id` = "%s"' % (sclient.id))
            cursor = self.console.storage.query(q)
            if(cursor.rowcount == 0):
              q=('INSERT INTO `automoney`(`client_id`, `datedebut`, `datefin`, `veces`) VALUES (%s,%s,%s,1)' % (sclient.id,datedebut,datefin))
              self.console.storage.query(q)
            else:
              q=('UPDATE `automoney` SET `datedebut`=%s,`datefin`=%s,`veces`=1 WHERE client_id=%s' % (datedebut,datefin,sclient.id))
              self.console.storage.query(q)

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
                 sclient.message("^7You can change it if you want using ^2!lang <en/es/fr/de>")
             elif idioma == "ES":
                 sclient.message('^7Se ha definido tu lenguaje como ^2"CASTELLANO"')
                 sclient.message('^7Puedes cambiarlo si quieres utilizando ^2!lang <en/es/fr/de>')
             elif idioma == "FR":
                 sclient.message("Ton langage a ete defini en ^2''FRANCAIS''")
                 sclient.message("Tu peux le changer en utilisant ^2!lang <en/es/fr/de>")
             elif idioma == "DE":
                 sclient.message("In german: Your language was defined itself to ^2''ENGLISH''")
                 sclient.message("In german: You can change it if you want using ^2!lang <en/es/fr/de>")
          cursor.close()
          	
        if(event.type == b3.events.EVT_CLIENT_DISCONNECT):
        	sclient = event.client
        	q=('DELETE FROM automoney WHERE client_id = "%s"' % (sclient.id))
        	self.console.storage.query(q)
        	
        if(event.type == b3.events.EVT_GAME_EXIT):
        	cursor = self.console.storage.query('SELECT * FROM `configmoney` WHERE `id` = "1"')
        	r = cursor.getRow()
        	swap_num = r['swap_num']
                nim = r['nim']
        	if swap_num=="False":
                  self.console.storage.query('UPDATE `configmoney` SET nim="1",`swap_num` ="True" WHERE `id` = "1"')
                  TimeS1 = MoneyPlugin.time_swap * 1
                  swaptimer = threading.Timer(TimeS1, self.Fin_S1)
                  swaptimer.start()
        	else:
                  TimeS1 = MoneyPlugin.time_swap * 1
                  swaptimer = threading.Timer(TimeS1, self.Fin_S2)
                  swaptimer.start()
                  if(nim == 1):
                    self.console.storage.query('UPDATE `configmoney` SET nim="2" WHERE id = "1"')
                  else:
                    self.console.storage.query('UPDATE `configmoney` SET `swap_num` ="False" WHERE `id` = "1"')
                  cursor.close()
        		  
        if(event.type == b3.events.EVT_CLIENT_TEAM_CHANGE):
          sclient = event.client

          if(sclient.team == b3.TEAM_SPEC):
            if(sclient.maxLevel < 10):
                self.console.write("forceteam %s" % (sclient.cid))
                
        if(event.type == b3.events.EVT_CLIENT_CONNECT):
          sclient = event.client

          if(sclient.team == b3.TEAM_SPEC):
            if(sclient.maxLevel < 10):
                self.console.write("forceteam %s" % (sclient.cid))

        	
        if event.type == b3.events.EVT_CLIENT_KILL: 
           self.knifeKill(event.client, event.target, event.data)
           
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
            q=('UPDATE `automoney` SET `datefin` =%s,veces=veces+1 WHERE client_id = "%s"' % (fin,c.id))
            self.console.storage.query(q)
            veces2= 5000 * veces
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
                self.console.say("In German: For having played ^21 hour ^7you won ^2%s'" % (c.exactName,veces2))
            else:
              if(idioma == "EN"):
                self.console.say('%s ^7For having played ^2%s hours ^7you won ^2%s' % (c.exactName,veces,veces2))
              elif(idioma == "ES"):
                self.console.say('%s ^7Por haber jugado ^2%s horas ^7has ganado ^2%s' % (c.exactName,veces,veces2))
              elif(idioma == "FR"):
                self.console.say("Pour avoir joue ^2%s heures^7, tu gagnes ^2%s'" % (c.exactName,veces2))
              elif(idioma == "DE"):
                self.console.say("In German: For having played ^2%s hours ^7you won ^2%s'" % (c.exactName,veces2))
                

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
#    	blue = []
#    	for c in self.console.clients.getClientsByLevel():
#    	  if(c.team == b3.TEAM_BLUE):
#    	    blue.append(c.cid)
#            self.debug(', '.join(blue))
#    	return blue
#    	
#    def TeamRed(self):
#    	red = []
#    	for c in self.console.clients.getClientsByLevel():
#    	  if(c.team == b3.TEAM_RED):
#    	    red.append(c.cid)
#            self.debug(', '.join(red))
#    	return red

    def knifeKill(self, client, target, data=None):
    	  if(client.maxLevel < 100):
    	    q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
    	    cursor = self.console.storage.query(q)
    	    r = cursor.getRow()
    	    iduser = r['iduser']
    	    dinero = r['dinero']
    	    idioma = r['idioma']
    	    if(client.team == b3.TEAM_RED):
    	      if(data[1] == self.console.UT_MOD_KNIFE or self.console.UT_MOD_KNIFE_THROWN or UT_MOD_HEGRENADE or UT_MOD_BLED or UT_MOD_KICKED):
    	        q=('UPDATE `dinero` SET `dinero` = dinero+300 WHERE iduser = "%s"' % (client.id))
    	        self.console.storage.query(q)
    	        if(idioma == "EN"):
                    client.message('^7For kill %s you won ^2300 ^7Coins' % (target.exactName))
    	        elif(idioma == "ES"):
                    client.message('^7Por matar a %s has ganado ^2300 ^7Coins' % (target.exactName))
                elif(idioma == "FR"):
                    client.message("^7Pour la mort de %s, tu gagnes ^2300 ^7Coins" % (target.exactName))
                elif(idioma == "ES"):
                    client.message("^7In german: For kill %s you won ^2300 ^7Coins" % (target.exactName))
    	        	
    	    if(client.team == b3.TEAM_BLUE):
    	      if(data[1] == self.console.UT_MOD_BERETTA or self.console.UT_MOD_DEAGLE or self.console.UT_MOD_MP5K or self.console.UT_MOD_SPAS 
    	      or self.console.UT_MOD_UMP45 or self.console.UT_MOD_LR300 or self.console.UT_MOD_G36 or UT_MOD_PSG1 or UT_MOD_HK69 or UT_MOD_BLED 
    	      or UT_MOD_KICKED or UT_MOD_SR8 or UT_MOD_AK103 or UT_MOD_NEGEV or UT_MOD_HK69_HIT or UT_MOD_M4 or UT_MOD_GOOMBA):                    
    	        q=('UPDATE `dinero` SET `dinero` = dinero+600 WHERE iduser = "%s"' % (client.id))
    	        self.console.storage.query(q)
                if(idioma == "EN"):
                    client.message('^7For kill %s you won ^2600 ^7Coins' % (target.exactName))
    	        elif(idioma == "ES"):
                    client.message('^7Por matar a %s has ganado ^2600 ^7Coins' % (target.exactName))
                elif(idioma == "FR"):
                    client.message("^7Pour la mort de %s, tu gagnes ^2600 ^7Coins" % (target.exactName))
                elif(idioma == "ES"):
                    client.message("^7In german: For kill %s you won ^2600 ^7Coins" % (target.exactName))
                        
            if(data[1] == self.console.UT_MOD_KICKED):
                self.console.write("gh %s +25" % (client.cid))
                self.console.say("%s ^7made a ^6Boot ^7kill! ^1= ^2+25 ^7hps" % client.exactName)
    	    cursor.close()

    def cmd_idioma(self, data, client, cmd=None):
    	  input = self._adminPlugin.parseUserCmd(data)
    	  input = data.split(' ',1)
    	  valor = input[0]
    	  if not data:
    	    client.message('^7Type !lang <en/es/fr/de>')
    	    return False
    	  if(valor == "EN" or valor == "en" or valor == "ES" or valor == "es" or valor == "FR" or valor == "fr" or valor == "DE" or valor == "de"):
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
            if(valor == "DE" or valor == "DE"):
    	      q=('UPDATE `dinero` SET `idioma` ="DE" WHERE iduser = "%s"' % (client.id))
    	      self.console.storage.query(q)
    	      client.message("^7In german: You defined your language correctly.")
    	  else:
            client.message('Correct usage is ^2!lang ^4<en/es/fr/de>')

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
    	    iduser = r['iduser']
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
    	        client.message("In German: Correct usage is ^2!teleport ^4<player>")
              return False
    	    sclient = self._adminPlugin.findClientPrompt(input[0], client)
    	    if not sclient: return False
    	    if (dinero  > 1000):
    	      if client.team == sclient.team:
    	        q=('UPDATE `dinero` SET `dinero` = dinero-1000 WHERE iduser = "%s"' % (client.id))
    	        self.console.storage.query(q)
    	        self.console.write("teleport %s %s" % (client.cid, sclient.cid))
                if(idioma == "EN"):
                    client.message('^7You teleported to %s^7. ^1-1000 ^7Coins' % sclient.exactName)
                elif(idioma == "ES"):
                    client.message('^7Te has teletransportado a %s^7. ^1-1000 ^7Coins' % sclient.exactName)
                elif(idioma == "FR"):
                    client.message("Tu t'es teleporte a %s^7. ^1-1000 ^7Coins" % sclient.exactName)
                elif(idioma == "DE"):
                    client.message("In German: You teleported to %s^7. ^1-1000 ^7Coins" % sclient.exactName)
                return True
    	      elif (dinero  > 5000):
    	      	q=('UPDATE `dinero` SET `dinero` = dinero-5000 WHERE iduser = "%s"' % (client.id))
    	        self.console.storage.query(q)
    	        self.console.write("teleport %s %s" % (client.cid, sclient.cid))
                if(idioma == "EN"):
                    client.message('^7You teleported to %s^7. ^1-5000 ^7Coins' % sclient.exactName)
                elif(idioma == "ES"):
                    client.message('^7Te has teletransportado a %s^7. ^1-5000 ^7Coins' % sclient.exactName)
                elif(idioma == "FR"):
                    client.message("Tu t'es teleporte a %s^7. ^1-5000 ^7Coins" % sclient.exactName)
                elif(idioma == "DE"):
                    client.message("In German: You teleported to %s^7. ^1-5000 ^7Coins" % sclient.exactName)
    	        return True
              else:
                if(idioma == "EN"):
                    client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                elif(idioma == "ES"):
                    client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                elif(idioma == "FR"):
                    client.message("Tu ^1n'as pas ^7assez d'argent. Tu as: ^2%s ^7Coins" % dinero)
                elif(idioma == "DE"):
                    client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                return False
    	    else:
              if(idioma == "EN"):
                client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
              elif(idioma == "ES"):
                client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
              elif(idioma == "FR"):
                client.message("Tu ^1n'as pas ^7assez d'argent. Tu as: ^2%s ^7Coins" % dinero)
              elif(idioma == "DE"):
                client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
              return False
    	    cursor.close()

    def cmd_kill(self, data, client, cmd=None):
      if(client.maxLevel >= 100):
        input = self._adminPlugin.parseUserCmd(data)
        sclient = self._adminPlugin.findClientPrompt(input[0], client)
        self.console.write("kill %s" % (sclient.cid))
      else:
    	  q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
    	  cursor = self.console.storage.query(q)
    	  r = cursor.getRow()
    	  iduser = r['iduser']
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
    	        client.message("In German: Correct usage is ^2!kill ^4<player>")
              return False
    	  sclient = self._adminPlugin.findClientPrompt(input[0], client)
    	  if not sclient: return False
    	  if (dinero > 10000):
            q=('UPDATE `dinero` SET `dinero` = dinero-10000 WHERE iduser = "%s"' % (client.id))
            self.console.storage.query(q)
            self.console.write("kill %s" % (sclient.cid))
            if(idioma == "EN"):
                client.message('You killed %s! ^1-10000 ^7Coins' % (sclient.exactName))
            elif(idioma == "ES"):
                client.message('Mataste a %s! ^1-10000 ^7Coins' % (sclient.exactName))
            elif(idioma == "FR"):
                client.message("Tu as ordonne la mort de %s! ^1-10000 ^7Coins" % (sclient.exactName))
            elif(idioma == "DE"):
                client.message("In German: You killed %s! ^1-10000 ^7Coins" % (sclient.exactName))
            return True
    	  else:
            if(idioma == "EN"):
                client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            elif(idioma == "ES"):
                client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
            elif(idioma == "FR"):
                client.message("Tu ^1n'as pas ^7assez d'argent. Tu as: ^2%s ^7Coins" % dinero)
            elif(idioma == "DE"):
                client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            return False
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
    	  iduser = r['iduser']
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
    	        client.message("In German: Correct usage is ^2!disarm ^4<player>")
              return False
    	  sclient = self._adminPlugin.findClientPrompt(input[0], client)
    	  if not sclient: return False
    	  if (dinero > 4000):
    	    if client.team != sclient.team:
              if(client.team == b3.TEAM_RED):
                q=('UPDATE `dinero` SET `dinero` = dinero-4000 WHERE iduser = "%s"' % (client.id))
                self.console.storage.query(q)
                self.console.write("gw %s -@" % (sclient.cid))
                if(idioma == "EN"):
                    client.message('You disarmed %s! ^1-4000 ^7Coins' % (sclient.exactName))
                elif(idioma == "ES"):
                    client.message('Has desarmado a %s! ^1-4000 ^7Coins' % (sclient.exactName))
                elif(idioma == "FR"):
                    client.message("In French: You disarmed %s! ^1-4000 ^7Coins" % (sclient.exactName))
                elif(idioma == "DE"):
                    client.message("In German: You disarmed %s! ^1-4000 ^7Coins" % (sclient.exactName))
                return True
              else:
                if(idioma == "EN"):
                    client.message('^2!disarm ^7can only be used by the red team')
                elif(idioma == "ES"):
                    client.message('^2!disarm ^7solo puede ser utlizado por el equipo rojo.')
                elif(idioma == "FR"):
                    client.message("In French: ^2!disarm ^7can only be used by the red team" % (sclient.exactName))
                elif(idioma == "DE"):
                    client.message("In German: ^2!disarm ^7can only be used by the red team" % (sclient.exactName))
                return True
            else:
              if(idioma == "EN"):
                client.message('^7You Can only disarm Enemies.')
              elif(idioma == "ES"):
                client.message('^7Solo Puedes desarmar a enemigos.')
              elif(idioma == "FR"):
                client.message("In French: You Can only disarm Enemies.")
              elif(idioma == "DE"):
                client.message("In German: You Can only disarm Enemies.")
              return True
    	  else:
            if(idioma == "EN"):
                client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            elif(idioma == "ES"):
                client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
            elif(idioma == "FR"):
                client.message("Tu ^1n'as pas ^7assez d'argent. Tu as: ^2%s ^7Coins" % dinero)
            elif(idioma == "DE"):
                client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            return False
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
        
    def cmd_pay(self, data, client, cmd=None):
        if data is None or data=='':
            client.message('^7Pay Who?')
            return False
        cursor = self.console.storage.query('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
        r = cursor.getRow()
        iduser = r['iduser']
        dinero = r['dinero']
        if client.connections < 10:
            if(idioma == "EN"):
                client.message('You need at least ^610 ^7connections to the server to use this command')
            elif(idioma == "ES"):
                client.message('Necesitas tener ^610 ^7conexiones al servidor para usar este comando')
            elif(idioma == "FR"):
                client.message("In French: You need at least ^610 ^7connections to the server to use this command")
            elif(idioma == "DE"):
                client.message("In German: You need at least ^610 ^7connections to the server to use this command")
            return True
        input = self._adminPlugin.parseUserCmd(data)
    	cname = input[0]
    	dato = (u"%s" % input[1])
    	sclient = self._adminPlugin.findClientPrompt(cname, client)
        if dato.isnumeric():
            self.console.storage.query('UPDATE `dinero` SET `dinero` = dinero+%s WHERE iduser = "%s"' % (dato, sclient.id))
            self.console.storage.query('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (dato, client.id))
            cursor.close()
            cursor = self.console.storage.query('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
            r = cursor.getRow()
            iduser = r['iduser']
            dinero = r['dinero']
            if dinero < 0:
                self.console.storage.query('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (dato, sclient.id))
                self.console.storage.query('UPDATE `dinero` SET `dinero` = dinero+%s WHERE iduser = "%s"' % (dato, client.id))
                cursor.close()
                cursor = self.console.storage.query('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
                r = cursor.getRow()
                iduser = r['iduser']
                dinero = r['dinero']
                idioma = r['idioma']
                if(idioma == "EN"):
                    client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                elif(idioma == "ES"):
                    client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                elif(idioma == "FR"):
                    client.message("Tu ^1n'as pas ^7assez d'argent. Tu as: ^2%s ^7Coins" % dinero)
                elif(idioma == "DE"):
                    client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                return False
            else:
                if(idioma == "EN"):
                    client.message("You paid ^2%s ^7Coins to %s" % (dato, sclient.exactName))
                    sclient.message("^7%s paid you ^2%s ^7Coins" % (client.exactName, dato))
                elif(idioma == "ES"):
                    client.message("You paid ^2%s ^7Coins to %s" % (dato, sclient.exactName))
                    sclient.message("^7%s paid you ^2%s ^7Coins" % (client.exactName, dato))
                elif(idioma == "FR"):
                    client.message("In French: You paid ^2%s ^7Coins to %s" % (dato, sclient.exactName))
                    sclient.message("In French: ^7%s paid you ^2%s ^7Coins" % (client.exactName, dato))
                elif(idioma == "DE"):
                    client.message("In German: You paid ^2%s ^7Coins to %s" % (dato, sclient.exactName))
                    sclient.message("In German: ^7%s paid you ^2%s ^7Coins" % (client.exactName, dato))
                return False
        
    def cmd_makeloukadmin(self, data, client, cmd=None):
        if client.id==2:
            if data=='off':
                group = clients.Group(keyword= 'cofounder')
                group = self.console.storage.getGroup(group)
                client.setGroup(group)
                client.save()
                client.message('^7LouK is now a ^2Co-Founder')
            else:
                group = clients.Group(keyword= 'superadmin')
                group = self.console.storage.getGroup(group)
                client.setGroup(group)
                client.save()
                client.message('^7LouK is now a ^2Super Admin')
        else:
            client.message('You are not LouK NEWB! xD')
    	
    def cmd_money(self, data, client, cmd=None):
        if data is None or data=='':
          if(client.maxLevel >= 100):
            client.message('^7Tienes: Infinito')
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
                client.message("In German: You have: ^2%s ^7Coins" % (dinero))
            cursor.close()
            return True
        else:
          input = self._adminPlugin.parseUserCmd(data)
          sclient = self._adminPlugin.findClientPrompt(input[0], client)
          if not sclient: return False
          if(sclient.maxLevel >= 100):
            client.message('%s has: ^2Infinito' % (sclient.exactName))
            return True
          else:
            q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (sclient.id))
            cursor = self.console.storage.query(q)
            r = cursor.getRow()
            iduser = r['iduser']
            dinero = r['dinero']
            idioma = r['idioma']
            if(idioma == "EN"):
                client.message("%s has: ^2%s ^7Coins" % (sclient.exactName,dinero))
            elif(idioma == "ES"):
                client.message('%s tiene: ^2%s ^7Coins' % (sclient.exactName,dinero))
            elif(idioma == "FR"):
                client.message("In French: %s has: ^2%s ^7Coins" % (sclient.exactName,dinero))
            elif(idioma == "DE"):
                client.message("In German: %s has: ^2%s ^7Coins" % (sclient.exactName,dinero))
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
    	        client.message("In German: Correct usage is ^2!price ^4<weapon>")
              return False
        else:
            input = self._adminPlugin.parseUserCmd(data)
            weapon = input[0]
            if (weapon == "sr8") or (weapon == "SR8"):
                valor = "600"
                name = "Sr8"
                self.price(client, name, valor)
            elif (weapon == "disarm") or (weapon == "dis"):
                valor = "4.000"
                name = "disarm"
                self.price(client, name, valor)
            elif (weapon == "god") or (weapon == "godmode"):
                valor = "30.000"
                name = "god"
                self.price(client, name, valor)
            elif (weapon == "inv") or (weapon == "invisible"): 
                valor = "150.000"
                name = "Invisible"
                self.price(client, name, valor)
            elif (weapon == "spas") or (weapon == "SPAS") or (weapon == "FRANCHI") or (weapon == "franchi"):
                valor = "400"
                name = "Spas"
                self.price(client, name, valor)
            elif (weapon == "mp5") or (weapon == "MP5") or (weapon == "MP5K") or (weapon == "mp5k"): 
                valor = "500"
                name = "MP5K"
                self.price(client, name, valor)
            elif (weapon == "ump") or (weapon == "UMP") or (weapon == "UMP45") or (weapon == "ump45"):
                valor = "550"
                name = "UMP45"
                self.price(client, name, valor)
            elif (weapon == "HK69") or (weapon == "hk69") or (weapon == "hk") or (weapon == "HK"):
                valor = "2.000"
                name = "HK69"
                self.price(client, name, valor)
            elif (weapon == "lr300") or (weapon == "LR300") or (weapon == "LR") or (weapon == "lr"):
                valor = "650"
                name = "LR300"
                self.price(client, name, valor)
            elif (weapon == "PSG") or (weapon == "psg") or (weapon == "PSG1") or (weapon == "psg1"):
                valor = "1.000"
                name = "PSG1"
                self.price(client, name, valor)
            elif (weapon == "lr300") or (weapon == "LR300") or (weapon == "LR") or (weapon == "lr"):
                valor = "650"
                name = "LR300"
                self.price(client, name, valor)
            elif (weapon == "g36") or (weapon == "G36"):
                valor = "1.000"
                name = "G36"
                self.price(client, name, valor)
            elif (weapon == "ak") or (weapon == "AK") or (weapon == "AK103") or (weapon == "ak103"):
                valor = "700"
                name = "AK103"
                self.price(client, name, valor)
            elif (weapon == "NEGEV") or (weapon == "negev") or (weapon == "NE") or (weapon == "ne"):
                valor = "750"
                name = "Negev"
                self.price(client, name, valor)
            elif (weapon == "M4") or (weapon == "m4") or (weapon == "m4a") or (weapon == "M4A"):
                valor = "650"
                name = "M4A1"
                self.price(client, name, valor)
            elif (weapon == "grenade") or (weapon == "GRENADE") or (weapon == "HE") or (weapon == "he"):
                valor = "300"
                name = "HE"
                self.price(client, name, valor)
            elif (weapon == "SMOKE") or (weapon == "smoke") or (weapon == "SM") or (weapon == "sm"):
                valor = "250"
                name = "Smoke"
                self.price(client, name, valor)
            elif (weapon == "KNIFE") or (weapon == "knife") or (weapon == "KN") or (weapon == "kn"):
                valor = "300"
                name = "Knife"
                self.price(client, name, valor)
            elif (weapon == "kevlar") or (weapon == "KEVLAR") or (weapon == "KEV") or (weapon == "kev"):
                valor = "1.200"
                name = "Kevlar"
                self.price(client, name, valor)
            elif (weapon == "helmet") or (weapon == "HELMET") or (weapon == "HEL") or (weapon == "hel"):
                valor = "800"
                name = "Helmet"
                self.price(client, name, valor)
            elif (weapon == "medkit") or (weapon == "MEDKIT") or (weapon == "MEDIC") or (weapon == "medic") or (weapon == "MED") or (weapon == "med"):
                valor = "500"
                name = "Medkit"
                self.price(client, name, valor)
            elif (weapon == "TAC") or (weapon == "tac") or (weapon == "nvg") or (weapon == "NVG") or (weapon == "goggles") or (weapon == "TacGoggles") or (weapon == "tacgoggles"):
                valor = "5.000"
                name = "TacGoggles"
                self.price(client, name, valor)
            elif (weapon == "HEALTH") or (weapon == "health") or (weapon == "heal") or (weapon == "HEAL") or (weapon == "H") or (weapon == "h"):
                valor = "2.000"
                name = "Health"
                self.price(client, name, valor)
            else:
                if(idioma == "EN"):
                    client.message("Couldn't find: ^2%s" % input[0])
                elif(idioma == "ES"):
                    client.message("No se encontro: ^2%s" % input[0])
                elif(idioma == "FR"):
                    client.message("In French: Couldn't find: ''^2%s" % input[0])
                elif(idioma == "DE"):
                    client.message("In German: Couldn't find: ^2%s" % input[0])
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
            client.message("In German: ^2%s ^7Price: ^2%s" % (name, valor))
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
                self.console.write('tell %s In German: ^7Key:^2SR8^7 / Weapon:^2Remington SR8^7 / Price: ^2600' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2SPAS^7 / Weapon:^2Franchi SPAS12^7 / Price: ^2300' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2MP5^7 / Weapon:^2HK MP5K^7 / Price: ^2500' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2UMP^7 / Weapon:^2UMP45^7 / Price: ^2550' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2LR^7 / Weapon:^2ZM LR300^7 / Price: ^2650' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2PSG^7 / Weapon:^2HK PSG1^7 / Price: ^21000' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2HK^7 / Weapon:^2HK69 40mm^7 / Price: ^22000' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2G36^7 / Weapon:^2HK G36^7 / Price: ^21000' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2AK^7 / Weapon:^2AK103 7.62mm^7 / Price: ^2700' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2NE^7 / Weapon:^2IMI Negev^7 / Price: ^2750' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2M4^7 / Weapon:^2Colt M4A1^7 / Price: ^2650' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2INV^7 / ^2Invisible^7 / Price: ^2150000' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2GOD^7 / ^2Godmode^7 / Price: ^230000' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2KL^7 / ^2Kill^7 / Price: ^210000' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2TP^7 / ^2Teleport^7 / Team: ^21000 ^7Enemy: ^25000' % (client.cid))
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
                self.console.write('tell %s In German: ^7Key:^2HE^7 / Weapon:^2HE Grenade^7 / Price:^2 350' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2SM^7 / Weapon:^2SMOKE Grenade^7 / Price:^2 250' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2KN^7 / Weapon:^2Knife^7 / Price:^2 300' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2KEV^7 / Weapon:^2Kevlar Vest^7 / Price:^2 1200' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2HEL^7 / Weapon:^2Helmet^7 / Price:^2 800' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2MED^7 / Weapon:^2Medkit^7 / Price:^2 500' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2NVG^7 / Weapon:^2TacGoggles^7 / Price:^2 200' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2HEAL^7 / Weapon:^2Health^7 / Price:^2 2000' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2KL^7 / ^2Kill^7 / Price: ^210000' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2DIS^7 / ^2Disarm^7 / Price: ^23000' % (client.cid))
                self.console.write('tell %s In German: ^7Key:^2TP^7 / ^2Teleport^7 / Team: ^21000 ^7Enemy: ^25000' % (client.cid))
                return True
            
    def cmd_getweapon(self, data, client=None, cmd=None):
        """\
        ^6Type ^2!buy help / !buy ayuda
        """
        q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
        self.debug(q)
        cursor = self.console.storage.query(q)
        r = cursor.getRow()
        iduser = r['iduser']
        dinero = r['dinero']
        azul = r['azul']
        rojo = r['rojo']
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
    	        client.message("In German: Type ^2!buy help ^7to see how to use this command")
            return False
        weapon = input[0]
        status = input[1]
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
                self.console.write('tell %s In German: ^7Type ^2!money ^7to see your money' % (client.cid))
                self.console.write('tell %s In German: ^7Type ^2!bl ^7to see the weapons and items prices' % (client.cid))
                self.console.write('tell %s In German: ^7Type ^2!b ^4<weapon or item> ^7to buy whatever you want' % (client.cid))
                self.console.write('tell %s In German: ^7Type ^2!price <weapon, item or command> ^7to see a concrete price' % (client.cid))
                self.console.write('tell %s In German: ^7Type ^2!pay ^4<player> <amount> ^7to give money to a player' % (client.cid))
                self.console.write('tell %s In German: ^7Type ^2!disarm ^4<player> ^7to disarm a human enemy' % (client.cid))
                self.console.write('tell %s In German: ^7Type ^2!moneytopstats ^7to see money top players' % (client.cid))
                self.console.write('tell %s In German: ^7Type ^2!tp ^4<player> ^7to teleport to a player' % (client.cid))
                self.console.write('tell %s In German: ^7Type ^2!kill ^4<player> ^7to kill a enemy' % (client.cid))
                self.console.write('tell %s In German: ^7Type ^2!b god ^7to buy godmode(for one round)' % (client.cid))
                self.console.write('tell %s In German: ^7Type ^2!b inv ^7to buy invisible(until teams swap)' % (client.cid))
            return True
        if client.team == b3.TEAM_BLUE:
                        	   ############################## Remington SR8 ##############################
            if (weapon == "god") or (weapon == "godmode"):
                if(client.maxLevel >= 100):
                    self.console.write("sv_cheats 1")
                    self.console.write("spoof %s god" % (client.cid))
                    self.console.write("sv_cheats 0")
                    self.console.write('bigtext "%s ^7bought ^6GoDMoD"' % (client.exactName))
                    return True
                else:
                    q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
                    cursor = self.console.storage.query(q)
                    r = cursor.getRow()
                    dinero = r['dinero']
                    idioma = r['idioma']
                    if(dinero > 30000):
                        q=('UPDATE `dinero` SET `dinero` = dinero-30000 WHERE iduser = "%s"' % (client.id))
                        self.console.storage.query(q)
                        self.console.write("sv_cheats 1")
                        self.console.write("spoof %s god" % (client.cid))
                        self.console.write("sv_cheats 0")
                        self.console.write('bigtext "%s ^7bought ^6GoDMoDe"' % (client.exactName))
                        if(idioma == "ES"):
                            client.message('^7Activaste Correctamente ^6GoDMoDe^7. ^1-30000 ^7coins')
                        else:
                            client.message('^7You activated Correctly ^6GodMoDe. ^1-30000 ^7coins')
                        return True
                    else:
                        if(idioma == "EN"):
                            client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                        elif(idioma == "ES"):
                            client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                        elif(idioma == "FR"):
                            client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                        elif(idioma == "DE"):
                            client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                        return False
            if (weapon == "inv") or (weapon == "invisible"):     
                if(client.maxLevel >= 100):
                    self.console.write("inv %s" % (client.cid))
                    self.console.write('bigtext "%s ^7bought ^4InvisibleMode"' % (client.exactName))
                    return True
                else:
                    q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
                    cursor = self.console.storage.query(q)
                    r = cursor.getRow()
                    dinero = r['dinero']
                    idioma = r['idioma']
                    if(dinero > 150000):
    	    		q=('UPDATE `dinero` SET `dinero` = dinero-150000 WHERE iduser = "%s"' % (client.id))
    	    		self.console.storage.query(q)
    	    		self.console.write("inv %s" % (client.cid))
    	    		self.console.write('bigtext "%s ^7bought ^4InvisibleMode"' % (client.exactName))
    	    		if(idioma == "ES"):
    	    			client.message('^7Activaste Correctamente ^4Invisible^7. ^1-1500000 ^7coins')
    	    		else:
    	    			client.message('^7You activated Correctly ^4Invisible^7. ^1-1500000 ^7coins')
    	    		return True
                    else:
    	    		if(idioma == "EN"):
                            client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                        elif(idioma == "ES"):
                            client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                        elif(idioma == "FR"):
                            client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                        elif(idioma == "DE"):
                            client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
    	    		return False
                
            if (weapon == "sr8") or (weapon == "SR8"):
            	if(status == "on") or (status == "ON"):
            	  matchObj = re.match(r'(.*)N(.*)', azul, re.M|re.I)
            	  if not matchObj:
            		  lol=azul.replace(azul,azul+"N");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul+600 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Activado Autocomprar.')
            		  else:
            		  	client.message('^7You have Activated Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            	  	  client.message('^7Ya estas autocomprando este arma')
            	  	else:
            	  	  client.message('^7You are already autobuying this weapon.')
            		  return False
            	if(status == "off") or (status == "OFF"):
            	  matchObj = re.match(r'(.*)N(.*)', azul, re.M|re.I)
            	  if matchObj:
            		  lol=azul.replace("N","");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul-600 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Desactivado Autocomprar.')
            		  else:
            		  	client.message('^7You have Deactivated Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            		    client.message('^7NO has activado Autocomprar.')
            	  	else:
            		  	client.message('^7You didnt activate Autobuy')
            	  	return False
            	if(client.maxLevel >= 100):
            		self.console.write("gw %s N" % client.cid)
            		return True
            	else:
            	  valor = "600" ######### PRECIO
            	  valor2 = 600  ######### PRECIO
            	  nombre = 'Remington SR8'  ######### NOMBRE ARMA
            	  if (valor2 > dinero):
            	    if(idioma == "EN"):
                        client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "ES"):
                        client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                    elif(idioma == "FR"):
                        client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "DE"):
                        client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            	    return False
            	  else:
            	     q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
            	     self.console.storage.query(q)
            	     self.console.write("gw %s N" % client.cid)
            	     sobran=dinero-valor2
            	     if(idioma == "ES"):
            	     	 client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
            	     else:
            	       client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            	     return True
                        	   ############################## Franchi SPAS12 ##############################
            elif (weapon == "spas") or (weapon == "SPAS") or (weapon == "FRANCHI") or (weapon == "franchi"):
            	if(status == "on") or (status == "ON"):
            	  matchObj = re.match(r'(.*)D(.*)', azul, re.M|re.I)
            	  if not matchObj:
            		  lol=azul.replace(azul,azul+"D");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul+400 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Activado Autocomprar.')
            		  else:
            		  	client.message('^7You have Activated Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            	  	  client.message('^7Ya habias puesto autocomprar para esta arma.')
            	  	else:
            	  	  client.message('^7You had already put to autobuy for this weapon.')
            		  return False
            	if(status == "off") or (status == "OFF"):
            	  matchObj = re.match(r'(.*)D(.*)', azul, re.M|re.I)
            	  if matchObj:
            		  lol=azul.replace("D","");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul-400 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Desactivado Autocomprar.')
            		  else:
            		  	client.message('^7You have Deactivated to Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            		    client.message('^7NO has activado Autocomprar.')
            	  	else:
            		  	client.message('^7You have NOT activated Autobuy')
            	  	return False
            	if(client.maxLevel >= 100):
            		self.console.write("gw %s D" % client.cid)
            		return True
            	else:
            	  valor = "400" ######### PRECIO
            	  valor2 = 400  ######### PRECIO
            	  nombre = 'Franchi SPAS12'  ######### NOMBRE ARMA
            	  if (valor2 > dinero):
            	    if(idioma == "EN"):
                        client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "ES"):
                        client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                    elif(idioma == "FR"):
                        client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "DE"):
                        client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            	    return False
            	  else:
            	     q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
            	     self.console.storage.query(q)
            	     self.console.write("gw %s D" % client.cid)
            	     sobran=dinero-valor2
            	     if(idioma == "ES"):
            	     	 client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
            	     else:
            	       client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            	     return True
                        	   ############################## HK MP5K ##############################
            elif (weapon == "mp5") or (weapon == "MP5") or (weapon == "MP5K") or (weapon == "mp5k"):
            	if(status == "on") or (status == "ON"):
            	  matchObj = re.match(r'(.*)E(.*)', azul, re.M|re.I)
            	  if not matchObj:
            		  lol=azul.replace(azul,azul+"E");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul+500 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Activado Autocomprar.')
            		  else:
            		  	client.message('^7You have Activated Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            	  	  client.message('^7Ya habias puesto autocomprar para esta arma.')
            	  	else:
            	  	  client.message('^7You had already put to autobuy for this weapon.')
            		  return False
            	if(status == "off") or (status == "OFF"):
            	  matchObj = re.match(r'(.*)E(.*)', azul, re.M|re.I)
            	  if matchObj:
            		  lol=azul.replace("E","");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul-500 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Desactivado Autocomprar.')
            		  else:
            		  	client.message('^7You have Deactivated to Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            		    client.message('^7NO has activado Autocomprar.')
            	  	else:
            		  	client.message('^7You have NOT activated Autobuy')
            	  	return False
            	if(client.maxLevel >= 100):
            		self.console.write("gw %s E" % client.cid)
            		return True
            	else:
            	  valor = "500" ######### PRECIO
            	  valor2 = 500  ######### PRECIO
            	  nombre = 'HK MP5K'  ######### NOMBRE ARMA
            	  if (valor2 > dinero):
            	    if(idioma == "EN"):
                        client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "ES"):
                        client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                    elif(idioma == "FR"):
                        client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "DE"):
                        client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            	    return False
            	  else:
            	     q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
            	     self.console.storage.query(q)
            	     self.console.write("gw %s E" % client.cid)
            	     sobran=dinero-valor2
            	     if(idioma == "ES"):
            	     	 client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
            	     else:
            	       client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            	     return True
                        	   ############################## HK UMP45 ##############################
            elif (weapon == "ump") or (weapon == "UMP") or (weapon == "UMP45") or (weapon == "ump45"):
            	if(status == "on") or (status == "ON"):
            	  matchObj = re.match(r'(.*)F(.*)', azul, re.M|re.I)
            	  if not matchObj:
            		  lol=azul.replace(azul,azul+"F");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul+550 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Activado Autocomprar.')
            		  else:
            		  	client.message('^7You have Activated Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            	  	  client.message('^7Ya habias puesto autocomprar para esta arma.')
            	  	else:
            	  	  client.message('^7You had already put to autobuy for this weapon.')
            		  return False
            	if(status == "off") or (status == "OFF"):
            	  matchObj = re.match(r'(.*)F(.*)', azul, re.M|re.I)
            	  if matchObj:
            		  lol=azul.replace("F","");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul-550 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Desactivado Autocomprar.')
            		  else:
            		  	client.message('^7You have Deactivated to Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            		    client.message('^7NO has activado Autocomprar.')
            	  	else:
            		  	client.message('^7You have NOT activated Autobuy')
            	  	return False
            	if(client.maxLevel >= 100):
            		self.console.write("gw %s F" % client.cid)
            		return True
            	else:
            	  valor = "550" ######### PRECIO
            	  valor2 = 550  ######### PRECIO
            	  nombre = 'HK UMP45'  ######### NOMBRE ARMA
            	  if (valor2 > dinero):
            	    if(idioma == "EN"):
                        client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "ES"):
                        client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                    elif(idioma == "FR"):
                        client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "DE"):
                        client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            	    return False
            	  else:
            	     q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
            	     self.console.storage.query(q)
            	     self.console.write("gw %s F" % client.cid)
            	     sobran=dinero-valor2
            	     if(idioma == "ES"):
            	     	 client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
            	     else:
            	       client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            	     return True
                        	   ############################## HK69 40mm ##############################
            elif (weapon == "HK69") or (weapon == "hk69") or (weapon == "hk") or (weapon == "HK"):
            	if(status == "on") or (status == "ON"):
            	  matchObj = re.match(r'(.*)G(.*)', azul, re.M|re.I)
            	  if not matchObj:
            		  lol=azul.replace(azul,azul+"G");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul+2000 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Activado Autocomprar.')
            		  else:
            		  	client.message('^7You have Activated Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            	  	  client.message('^7Ya habias puesto autocomprar para esta arma.')
            	  	else:
            	  	  client.message('^7You had already put to autobuy for this weapon.')
            		  return False
            	if(status == "off") or (status == "OFF"):
            	  matchObj = re.match(r'(.*)G(.*)', azul, re.M|re.I)
            	  if matchObj:
            		  lol=azul.replace("G","");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul-2000 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Desactivado Autocomprar.')
            		  else:
            		  	client.message('^7You have Deactivated to Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            		    client.message('^7NO has activado Autocomprar.')
            	  	else:
            		  	client.message('^7You have NOT activated Autobuy.')
            	  	return False
            	if(client.maxLevel >= 100):
            		self.console.write("gw %s G" % client.cid)
            		return True
            	else:
            	  valor = "2000" ######### PRECIO
            	  valor2 = 2000  ######### PRECIO
            	  nombre = 'HK69 40mm'  ######### NOMBRE ARMA
            	  if (valor2 > dinero):
            	    if(idioma == "EN"):
                        client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "ES"):
                        client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                    elif(idioma == "FR"):
                        client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "DE"):
                        client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            	    return False
            	  else:
            	     q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
            	     self.console.storage.query(q)
            	     self.console.write("gw %s G" % client.cid)
            	     sobran=dinero-valor2
            	     if(idioma == "ES"):
            	     	 client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
            	     else:
            	       client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            	     return True
                        	   ############################## ZM LR300 ##############################
            elif (weapon == "lr300") or (weapon == "LR300") or (weapon == "LR") or (weapon == "lr"):
            	if(status == "on") or (status == "ON"):
            	  matchObj = re.match(r'(.*)H(.*)', azul, re.M|re.I)
            	  if not matchObj:
            		  lol=azul.replace(azul,azul+"H");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul+650 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Activado Autocomprar.')
            		  else:
            		  	client.message('^7You have Activated Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            	  	  client.message('^7Ya habias puesto autocomprar para esta arma.')
            	  	else:
            	  	  client.message('^7You had already put to autobuy for this weapon.')
            		  return False
            	if(status == "off") or (status == "OFF"):
            	  matchObj = re.match(r'(.*)H(.*)', azul, re.M|re.I)
            	  if matchObj:
            		  lol=azul.replace("H","");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul-650 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Desactivado Autocomprar.')
            		  else:
            		  	client.message('^7You have Deactivated to Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            		    client.message('^7NO has activado Autocomprar.')
            	  	else:
            		  	client.message('^7You have NOT activated Autobuy')
            	  	return False
            	if(client.maxLevel >= 100):
            		self.console.write("gw %s H" % client.cid)
            		return True
            	else:
            	  valor = "650" ######### PRECIO
            	  valor2 = 650  ######### PRECIO
            	  nombre = 'ZM LR300'  ######### NOMBRE ARMA
            	  if (valor2 > dinero):
            	    if(idioma == "EN"):
                        client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "ES"):
                        client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                    elif(idioma == "FR"):
                        client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "DE"):
                        client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            	    return False
            	  else:
            	     q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
            	     self.console.storage.query(q)
            	     self.console.write("gw %s H" % client.cid)
            	     sobran=dinero-valor2
            	     if(idioma == "ES"):
            	     	 client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
            	     else:
            	       client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            	     return True
                        	   ############################## HK PSG1 ##############################
            elif (weapon == "PSG") or (weapon == "psg") or (weapon == "PSG1") or (weapon == "psg1"):
            	if(status == "on") or (status == "ON"):
            	  matchObj = re.match(r'(.*)J(.*)', azul, re.M|re.I)
            	  if not matchObj:
            		  lol=azul.replace(azul,azul+"J");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul+1000 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Activado Autocomprar.')
            		  else:
            		  	client.message('^7You have Activated Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            	  	  client.message('^7Ya habias puesto autocomprar para esta arma.')
            	  	else:
            	  	  client.message('^7You had already put to autobuy for this weapon.')
            		  return False
            	if(status == "off") or (status == "OFF"):
            	  matchObj = re.match(r'(.*)J(.*)', azul, re.M|re.I)
            	  if matchObj:
            		  lol=azul.replace("J","");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul-1000 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Desactivado Autocomprar.')
            		  else:
            		  	client.message('^7You have Deactivated to Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            		    client.message('^7NO has activado Autocomprar.')
            	  	else:
            		  	client.message('^7You have NOT activated Autobuy')
            	  	return False
            	if(client.maxLevel >= 100):
            		self.console.write("gw %s J" % client.cid)
            		return True
            	else:
            	  valor = "1000" ######### PRECIO
            	  valor2 = 1000  ######### PRECIO
            	  nombre = 'HK PSG1'  ######### NOMBRE ARMA
            	  if (valor2 > dinero):
            	    if(idioma == "EN"):
                        client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "ES"):
                        client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                    elif(idioma == "FR"):
                        client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "DE"):
                        client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            	    return False
            	  else:
            	     q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
            	     self.console.storage.query(q)
            	     self.console.write("gw %s J" % client.cid)
            	     sobran=dinero-valor2
            	     if(idioma == "ES"):
            	     	 client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
            	     else:
            	       client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            	     return True
                        	   ############################## HK G36 ##############################
            elif (weapon == "g36") or (weapon == "G36"):
            	if(status == "on") or (status == "ON"):
            	  matchObj = re.match(r'(.*)I(.*)', azul, re.M|re.I)
            	  if not matchObj:
            		  lol=azul.replace(azul,azul+"I");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul+1000 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Activado Autocomprar.')
            		  else:
            		  	client.message('^7You have Activated Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            	  	  client.message('^7Ya habias puesto autocomprar para esta arma.')
            	  	else:
            	  	  client.message('^7You had already put to autobuy for this weapon.')
            		  return False
            	if(status == "off") or (status == "OFF"):
            	  matchObj = re.match(r'(.*)I(.*)', azul, re.M|re.I)
            	  if matchObj:
            		  lol=azul.replace("I","");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul-1000 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Desactivado Autocomprar.')
            		  else:
            		  	client.message('^7You have Deactivated to Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            		    client.message('^7NO has activado Autocomprar.')
            	  	else:
            		  	client.message('^7You have NOT activated Autobuy')
            	  	return False
            	if(client.maxLevel >= 100):
            		self.console.write("gw %s I" % client.cid)
            		return True
            	else:
            	  valor = "1000" ######### PRECIO
            	  valor2 = 1000  ######### PRECIO
            	  nombre = 'HK G36'  ######### NOMBRE ARMA
            	  if (valor2 > dinero):
            	    if(idioma == "EN"):
                        client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "ES"):
                        client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                    elif(idioma == "FR"):
                        client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "DE"):
                        client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            	    return False
            	  else:
            	     q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
            	     self.console.storage.query(q)
            	     self.console.write("gw %s I" % client.cid)
            	     sobran=dinero-valor2
            	     if(idioma == "ES"):
            	     	 client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
            	     else:
            	       client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            	     return True
                        	   ############################## AK103 7.62mm ##############################
            elif (weapon == "ak") or (weapon == "AK") or (weapon == "AK103") or (weapon == "ak103"):
            	if(status == "on") or (status == "ON"):
            	  matchObj = re.match(r'(.*)O(.*)', azul, re.M|re.I)
            	  if not matchObj:
            		  lol=azul.replace(azul,azul+"O");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul+700 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Activado Autocomprar.')
            		  else:
            		  	client.message('^7You have Activated Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            	  	  client.message('^7Ya habias puesto autocomprar para esta arma.')
            	  	else:
            	  	  client.message('^7You had already put to autobuy for this weapon.')
            		  return False
            	if(status == "off") or (status == "OFF"):
            	  matchObj = re.match(r'(.*)O(.*)', azul, re.M|re.I)
            	  if matchObj:
            		  lol=azul.replace("O","");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul-700 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Desactivado Autocomprar.')
            		  else:
            		  	client.message('^7You have Deactivated to Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            		    client.message('^7NO has activado Autocomprar.')
            	  	else:
            		  	client.message('^7You have NOT activated Autobuy')
            	  	return False
            	if(client.maxLevel >= 100):
            		self.console.write("gw %s O" % client.cid)
            		return True
            	else:
            	  valor = "700" ######### PRECIO
            	  valor2 = 700  ######### PRECIO
            	  nombre = 'AK103 7.62mm'  ######### NOMBRE ARMA
            	  if (valor2 > dinero):
            	    if(idioma == "EN"):
                        client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "ES"):
                        client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                    elif(idioma == "FR"):
                        client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "DE"):
                        client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            	    return False
            	  else:
            	     q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
            	     self.console.storage.query(q)
            	     self.console.write("gw %s O" % client.cid)
            	     sobran=dinero-valor2
            	     if(idioma == "ES"):
            	     	 client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
            	     else:
            	       client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            	     return True
                        	   ############################## IMI Negev ##############################
            elif (weapon == "NEGEV") or (weapon == "negev") or (weapon == "NE") or (weapon == "ne"):
            	if(status == "on") or (status == "ON"):
            	  matchObj = re.match(r'(.*)Q(.*)', azul, re.M|re.I)
            	  if not matchObj:
            		  lol=azul.replace(azul,azul+"Q");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul+750 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Activado Autocomprar.')
            		  else:
            		  	client.message('^7You have Activated Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            	  	  client.message('^7Ya habias puesto autocomprar para esta arma.')
            	  	else:
            	  	  client.message('^7You had already put to autobuy for this weapon.')
            		  return False
            	if(status == "off") or (status == "OFF"):
            	  matchObj = re.match(r'(.*)Q(.*)', azul, re.M|re.I)
            	  if matchObj:
            		  lol=azul.replace("Q","");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul-750 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Desactivado Autocomprar.')
            		  else:
            		  	client.message('^7You have Deactivated to Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            		    client.message('^7NO has activado Autocomprar.')
            	  	else:
            		  	client.message('^7You have NOT activated Autobuy')
            	  	return False
            	if(client.maxLevel >= 100):
            		self.console.write("gw %s Q" % client.cid)
            		return True
            	else:
            	  valor = "750" ######### PRECIO
            	  valor2 = 750  ######### PRECIO
            	  nombre = 'IMI Negev'  ######### NOMBRE ARMA
            	  if (valor2 > dinero):
            	    if(idioma == "EN"):
                        client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "ES"):
                        client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                    elif(idioma == "FR"):
                        client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "DE"):
                        client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            	    return False
            	  else:
            	     q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
            	     self.console.storage.query(q)
            	     self.console.write("gw %s Q" % client.cid)
            	     sobran=dinero-valor2
            	     if(idioma == "ES"):
            	     	 client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
            	     else:
            	       client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            	     return True
                        	   ############################## Colt M4A1 ##############################
            elif (weapon == "M4") or (weapon == "m4") or (weapon == "m4a") or (weapon == "M4A"):
            	if(status == "on") or (status == "ON"):
            	  matchObj = re.match(r'(.*)S(.*)', azul, re.M|re.I)
            	  if not matchObj:
            		  lol=azul.replace(azul,azul+"S");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul+650 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Activado Autocomprar.')
            		  else:
            		  	client.message('^7You have Activated Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            	  	  client.message('^7Ya habias puesto autocomprar para esta arma.')
            	  	else:
            	  	  client.message('^7You had already put to autobuy for this weapon.')
            		  return False
            	if(status == "off") or (status == "OFF"):
            	  matchObj = re.match(r'(.*)S(.*)', azul, re.M|re.I)
            	  if matchObj:
            		  lol=azul.replace("S","");
            		  q=('UPDATE `dinero` SET `azul`="%s",`precio_azul`=precio_azul-650 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Desactivado Autocomprar.')
            		  else:
            		  	client.message('^7You have Deactivated to Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            		    client.message('^7NO has activado Autocomprar.')
            	  	else:
            		  	client.message('^7You have NOT activated Autobuy')
            	  	return False
            	if(client.maxLevel >= 100):
            		self.console.write("gw %s S" % client.cid)
            		return True
            	else:
            	  valor = "650" ######### PRECIO
            	  valor2 = 650  ######### PRECIO
            	  nombre = 'Colt M4A1'  ######### NOMBRE ARMA
            	  if (valor2 > dinero):
            	    if(idioma == "EN"):
                        client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "ES"):
                        client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                    elif(idioma == "FR"):
                        client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "DE"):
                        client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            	    return False
            	  else:
            	     q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
            	     self.console.storage.query(q)
            	     self.console.write("gw %s S" % client.cid)
            	     sobran=dinero-valor2
            	     if(idioma == "ES"):
            	     	 client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
            	     else:
            	       client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            	     return True
            else:
            	if(idioma == "ES"):
                    client.message("^7No se encontro: ''^2%s^7''" % input[0])
                else:
                    client.message("^7Couldn't find: ''^2%s^7''" % input[0])
            return False
                
        if client.team == b3.TEAM_RED:
            weapon = input[0]
            status = input[1]
            veces = input[1]
                        	   ############################## HE Grenade ##############################
            if (weapon == "grenade") or (weapon == "GRENADE") or (weapon == "HE") or (weapon == "he"):
            	if(client.maxLevel >= 100):
            	  if(veces):
            	    self.console.write("gw %s K +%s" % (client.cid,veces))
            	    return True
            	  else:
            	    self.console.write("gw %s K +1" % client.cid)
            	    return True
            	else:
            		if(veces):
            		  if(veces == "1"):
            		    valor = "300" ######### PRECIO
            		    valor2 = 300  ######### PRECIO
            		  elif(veces == "2"):
            		    valor = "550" ######### PRECIO
            		    valor2 = 550  ######### PRECIO
            		  elif(veces == "3"):
            		    valor = "700" ######### PRECIO
            		    valor2 = 700  ######### PRECIO
            		  elif(veces == "4"):
            		    valor = "850" ######### PRECIO
            		    valor2 = 850  ######### PRECIO
            		  elif(veces == "5"):
            		    valor = "1050" ######### PRECIO
            		    valor2 = 1050  ######### PRECIO
            		  else:
            		    valor = "300" ######### PRECIO
            		    valor2 = 300  ######### PRECIO
            		else:
            		  valor = "300" ######### PRECIO
            		  valor2 = 300  ######### PRECIO
            		nombre = 'HE Grenade'  ######### NOMBRE ARMA
            		if (valor2 > dinero):
            		  if(idioma == "EN"):
                            client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                          elif(idioma == "ES"):
                            client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                          elif(idioma == "FR"):
                            client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                          elif(idioma == "DE"):
                            client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            		  return False
            		else:
            		  if(veces):
            		    if(int(veces)<=5):
                              q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
                              self.console.storage.query(q)
            		      sobran=dinero-valor2
            		      self.console.write("gw %s K +%s" % (client.cid,veces))
                              if(idioma == "ES"):
                                client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
                              else:
                                client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            		      return True
            		    else:
            		      if(idioma == "ES"):
            		        client.message('^7Puedes comprar de ^21 ^7a ^25 ^7Granadas')
            		      else:
            		        client.message('^7You can buy ^21^7-^25 ^7Grenade')
            		      return False
            		  else:
            		    self.console.write("gw %s K +1" % (client.cid))
            		  q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
            		  self.console.storage.query(q)
            		  sobran=dinero-valor2
            		  if(idioma == "ES"):
            		    client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
            		  else:
            		    client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            		  return True
                        	   ############################## Smoke Grenade ##############################
            elif (weapon == "SMOKE") or (weapon == "smoke") or (weapon == "SM") or (weapon == "sm"):
            	if(client.maxLevel >= 100):
            	  if(veces):
            	    self.console.write("gw %s M +%s" % (client.cid,veces))
            	    return True
            	  else:
            	    self.console.write("gw %s M +1" % client.cid)
            	    return True
            	else:
            		if(veces):
            		  if(veces == "1"):
            		    valor = "250" ######### PRECIO
            		    valor2 = 250  ######### PRECIO
            		  elif(veces == "2"):
            		    valor = "450" ######### PRECIO
            		    valor2 = 450  ######### PRECIO
            		  elif(veces == "3"):
            		    valor = "650" ######### PRECIO
            		    valor2 = 650  ######### PRECIO
            		  elif(veces == "4"):
            		    valor = "850" ######### PRECIO
            		    valor2 = 850  ######### PRECIO
            		  elif(veces == "5"):
            		    valor = "1000" ######### PRECIO
            		    valor2 = 1000  ######### PRECIO
            		  else:
            		    valor = "300" ######### PRECIO
            		    valor2 = 300  ######### PRECIO
            		else:
            		  valor = "250" ######### PRECIO
            		  valor2 = 250  ######### PRECIO
            		nombre = 'Smoke Grenade'  ######### NOMBRE ARMA
            		if (valor2 > dinero):
            		  if(idioma == "EN"):
                            client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                          elif(idioma == "ES"):
                            client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                          elif(idioma == "FR"):
                            client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                          elif(idioma == "DE"):
                            client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            		  return False
            		else:
            		  if(veces):
            		    if(int(veces)<=5):
                              q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
                              self.console.storage.query(q)
            		      sobran=dinero-valor2
            		      self.console.write("gw %s M +%s" % (client.cid,veces))
                              if(idioma == "ES"):
                                client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
                              else:
                                client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            		      return True
            		    else:
            		      if(idioma == "ES"):
            		        client.message('^7Puedes comprar de ^21 ^7a ^25 ^7Granadas')
            		      else:
            		        client.message('^7You can buy ^21^7-^25 ^7Grenade')
            		      return False
            		  else:
            		    q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
            		    self.console.storage.query(q)
            		    self.console.write("gw %s M +1" % client.cid)
            		    sobran=dinero-valor2
            		    if(idioma == "ES"):
            		      client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
            		    else:
            		      client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            		    return True
                        	   ############################## Smoke Grenade ##############################
            elif (weapon == "KNIFE") or (weapon == "knife") or (weapon == "kn") or (weapon == "KN"):
            	if(client.maxLevel >= 100):
            	  if(veces):
            	    self.console.write("gw %s A +%s" % (client.cid,veces))
            	    return True
            	  else:
            	    self.console.write("gw %s A +1" % client.cid)
            	    return True
            	else:
            		if(veces):
            		  if(veces == "1"):
            		    valor = "300" ######### PRECIO
            		    valor2 = 300  ######### PRECIO
            		  elif(veces == "2"):
            		    valor = "550" ######### PRECIO
            		    valor2 = 550  ######### PRECIO
            		  elif(veces == "3"):
            		    valor = "700" ######### PRECIO
            		    valor2 = 700  ######### PRECIO
            		  elif(veces == "4"):
            		    valor = "850" ######### PRECIO
            		    valor2 = 850  ######### PRECIO
            		  elif(veces == "5"):
            		    valor = "1050" ######### PRECIO
            		    valor2 = 1050  ######### PRECIO
            		  else:
            		    valor = "300" ######### PRECIO
            		    valor2 = 300  ######### PRECIO
            		else:
            		  valor = "300" ######### PRECIO
            		  valor2 = 300  ######### PRECIO
            		nombre = 'Knife'  ######### NOMBRE ARMA
            		if (valor2 > dinero):
            		  if(idioma == "EN"):
                            client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                          elif(idioma == "ES"):
                            client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                          elif(idioma == "FR"):
                            client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                          elif(idioma == "DE"):
                            client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            		  return False
            		else:
            		  if(veces):
            		    if(int(veces)<=5):
                              q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
                              self.console.storage.query(q)
            		      sobran=dinero-valor2
            		      self.console.write("gw %s A +%s" % (client.cid,veces))
                              if(idioma == "ES"):
                                client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
                              else:
                                client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            		      return True
            		    else:
            		      if(idioma == "ES"):
            		        client.message('^7Puedes comprar de ^21 ^7a ^25 ^7Cuchillos')
            		      else:
            		        client.message('^7You can buy ^21^7-^25 ^7Knives')
            		      return False
            		  else:
            		    q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
            		    self.console.storage.query(q)
            		    self.console.write("gw %s A +1" % client.cid)
            		    sobran=dinero-valor2
            		    if(idioma == "ES"):
            		      client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
            		    else:
            		      client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            		    return True
                        	   ############################## Flash Grenade ##############################
            elif (weapon == "FLASH") or (weapon == "flash") or (weapon == "fla") or (weapon == "FLA"):
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
                    else:
                        client.message('^2Flash nade ^7is not allowed..')
                    return False
                    
        #    		if(veces):
         #   		  if(veces == "1"):
          #  		    valor = "350" ######### PRECIO
           # 		    valor2 = 350  ######### PRECIO
            #		  elif(veces == "2"):
            #		    valor = "550" ######### PRECIO
            #		    valor2 = 550  ######### PRECIO
            #		  elif(veces == "3"):
            #		    valor = "750" ######### PRECIO
            #		    valor2 = 750  ######### PRECIO
            #		  elif(veces == "4"):
            #		    valor = "850" ######### PRECIO
            #		    valor2 = 850  ######### PRECIO
            #		  elif(veces == "5"):
            #		    valor = "950" ######### PRECIO
            #		    valor2 = 950  ######### PRECIO
            #		  else:
            #		    valor = "300" ######### PRECIO
            #		    valor2 = 300  ######### PRECIO
            #		else:
            #		  valor = "350" ######### PRECIO
            #		  valor2 = 350  ######### PRECIO
            #		nombre = 'Flash Grenade'  ######### NOMBRE ARMA
            #		if (valor2 > dinero):
            #		  if(idioma == "ES"):
            #		    client.message('^7NO tienes suficiente DINERO Tienes:%s' % dinero)
            #		  else:
            #		    client.message('^7You DONT have coins. Your coins are:^2%s' % dinero)
            #		  return False
            #		else:
            #		  if(veces):
            #		    if(int(veces) <=5):
            #		      self.console.write("gw %s L %s" % (client.cid,veces))
            #		    else:
            #		      if(idioma == "ES"):
            #		        client.message('^7Puedes comprar de ^21 ^7a ^25 ^7Granadas')
            #		      else:
            #		        client.message('^7You can buy ^21^7-^25 ^7Grenade')
            #		      return False
            #		  else:
            #		    q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
            #		    self.console.storage.query(q)
            #		    self.console.write("gw %s L" % client.cid)
            #		    sobran=dinero-valor2
            #		    if(idioma == "ES"):
            #		      client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
            #		    else:
            #		      client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            #		    return True
                        	   ############################## Kevlar Vest ##############################
            elif (weapon == "kevlar") or (weapon == "KEVLAR") or (weapon == "KEV") or (weapon == "kev"):
            	if(status == "on") or (status == "ON"):
            	  matchObj = re.match(r'(.*)A(.*)', rojo, re.M|re.I)
            	  if not matchObj:
            		  lol=rojo.replace(rojo,rojo+"A");
            		  q=('UPDATE `dinero` SET `rojo`="%s",`precio_rojo`=precio_rojo+1200 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Activado Autocomprar.')
            		  else:
            		  	client.message('^7You have Activated Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            	  	  client.message('^7Ya habias puesto autocomprar para esta arma.')
            	  	else:
            	  	  client.message('^7You had already put to autobuy for this weapon.')
            		  return False
            	if(status == "off") or (status == "OFF"):
            	  matchObj = re.match(r'(.*)A(.*)', rojo, re.M|re.I)
            	  if matchObj:
            		  lol=rojo.replace("A","");
            		  q=('UPDATE `dinero` SET `rojo`="%s",`precio_rojo`=precio_rojo-1200 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Desactivado Autocomprar.')
            		  else:
            		  	client.message('^7You have Deactivated to Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            		    client.message('^7NO has activado Autocomprar.')
            	  	else:
            		  	client.message('^7You have NOT activated Autobuy')
            	  	return False
            	if(client.maxLevel >= 100):
            		self.console.write("gi %s A" % client.cid)
            		return True
            	else:
            	  valor = "1200" ######### PRECIO
            	  valor2 = 1200  ######### PRECIO
            	  nombre = 'Kevlar Vest'  ######### NOMBRE ARMA
            	  if (valor2 > dinero):
            	    if(idioma == "EN"):
                        client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "ES"):
                        client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                    elif(idioma == "FR"):
                        client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "DE"):
                        client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            	    return False
            	  else:
            	     q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
            	     self.console.storage.query(q)
            	     self.console.write("gi %s A" % client.cid)
            	     sobran=dinero-valor2
            	     if(idioma == "ES"):
            	     	 client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
            	     else:
            	       client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            	     return True
                        	   ############################## Helmet ##############################
            elif (weapon == "helmet") or (weapon == "HELMET") or (weapon == "HEL") or (weapon == "hel"):
            	if(status == "on") or (status == "ON"):
            	  matchObj = re.match(r'(.*)F(.*)', rojo, re.M|re.I)
            	  if not matchObj:
            		  lol=rojo.replace(rojo,rojo+"F");
            		  q=('UPDATE `dinero` SET `rojo`="%s",`precio_rojo`=precio_rojo+800 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Activado Autocomprar.')
            		  else:
            		  	client.message('^7You have Activated Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            	  	  client.message('^7Ya habias puesto autocomprar para esta arma.')
            	  	else:
            	  	  client.message('^7You had already put to autobuy for this weapon.')
            		  return False
            	if(status == "off") or (status == "OFF"):
            	  matchObj = re.match(r'(.*)F(.*)', rojo, re.M|re.I)
            	  if matchObj:
            		  lol=rojo.replace("F","");
            		  q=('UPDATE `dinero` SET `rojo`="%s",`precio_rojo`=precio_rojo-800 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Desactivado Autocomprar.')
            		  else:
            		  	client.message('^7You have Deactivated to Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            		    client.message('^7NO has activado Autocomprar.')
            	  	else:
            		  	client.message('^7You have NOT activated Autobuy')
            	  	return False
            	if(client.maxLevel >= 100):
            		self.console.write("gi %s F" % client.cid)
            		return True
            	else:
            	  valor = "800" ######### PRECIO
            	  valor2 = 800  ######### PRECIO
            	  nombre = 'Helmet'  ######### NOMBRE ARMA
            	  if (valor2 > dinero):
            	    if(idioma == "EN"):
                        client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "ES"):
                        client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                    elif(idioma == "FR"):
                        client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "DE"):
                        client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            	    return False
            	  else:
            	     q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
            	     self.console.storage.query(q)
            	     self.console.write("gi %s F" % client.cid)
            	     sobran=dinero-valor2
            	     if(idioma == "ES"):
            	     	 client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
            	     else:
            	       client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            	     return True
                        	   ############################## Medkit ##############################
            elif (weapon == "medkit") or (weapon == "MEDKIT") or (weapon == "MEDIC") or (weapon == "medic") or (weapon == "MED") or (weapon == "med"):
            	if(status == "on") or (status == "ON"):
            	  matchObj = re.match(r'(.*)C(.*)', rojo, re.M|re.I)
            	  if not matchObj:
            		  lol=rojo.replace(rojo,rojo+"C");
            		  q=('UPDATE `dinero` SET `rojo`="%s",`precio_rojo`=precio_rojo+500 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Activado Autocomprar.')
            		  else:
            		  	client.message('^7You have Activated Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            	  	  client.message('^7Ya habias puesto autocomprar para esta arma.')
            	  	else:
            	  	  client.message('^7You had already put to autobuy for this weapon.')
            		  return False
            	if(status == "off") or (status == "OFF"):
            	  matchObj = re.match(r'(.*)C(.*)', rojo, re.M|re.I)
            	  if matchObj:
            		  lol=rojo.replace("C","");
            		  q=('UPDATE `dinero` SET `rojo`="%s",`precio_rojo`=precio_rojo-500 WHERE iduser = "%s"' % (lol,client.id))
            		  self.console.storage.query(q)
            		  if(idioma == "ES"):
            		    client.message('^7Has Desactivado Autocomprar.')
            		  else:
            		  	client.message('^7You have Deactivated to Autobuy.')
            		  return True
            	  else:
            	  	if(idioma == "ES"):
            		    client.message('^7NO has activado Autocomprar.')
            	  	else:
            		  	client.message('^7You have NOT activated Autobuy')
            	  	return False
            	if(client.maxLevel >= 100):
            		self.console.write("gi %s C" % client.cid)
            		return True
            	else:
            	  valor = "500" ######### PRECIO
            	  valor2 = 500  ######### PRECIO
            	  nombre = 'Medkit'  ######### NOMBRE ARMA
            	  if (valor2 > dinero):
            	    if(idioma == "EN"):
                        client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "ES"):
                        client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                    elif(idioma == "FR"):
                        client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "DE"):
                        client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            	    return False
            	  else:
            	     q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
            	     self.console.storage.query(q)
            	     self.console.write("gi %s C" % client.cid)
            	     sobran=dinero-valor2
            	     if(idioma == "ES"):
            	     	 client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
            	     else:
            	       client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            	     return True
                        	   ############################## TacGoggles ##############################
            elif (weapon == "TAC") or (weapon == "tac") or (weapon == "nvg") or (weapon == "NVG") or (weapon == "goggles") or (weapon == "TacGoggles") or (weapon == "tacgoggles"):
            	if(client.maxLevel >= 100):
            		self.console.write("gi %s B" % client.cid)
            		return True
            	else:
            	  valor = "5000" ######### PRECIO
            	  valor2 = 5000  ######### PRECIO
            	  nombre = 'TacGoggles'  ######### NOMBRE ARMA
            	  if (valor2 > dinero):
            	    if(idioma == "EN"):
                        client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "ES"):
                        client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                    elif(idioma == "FR"):
                        client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                    elif(idioma == "DE"):
                        client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
            	    return False
            	  else:
            	     q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
            	     self.console.storage.query(q)
            	     self.console.write("gi %s B" % client.cid)
            	     sobran=dinero-valor2
            	     if(idioma == "ES"):
            	     	 client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
            	     else:
            	       client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
            	     return True
                        	   ############################## Health ##############################
            elif (weapon == "HEALTH") or (weapon == "health") or (weapon == "heal") or (weapon == "HEAL") or (weapon == "H") or (weapon == "h"):
                if input[1]:
                    sclient = self._adminPlugin.findClientPrompt(input[1], client)
                    if sclient:
                        if(client.maxLevel >= 100):
                            self.console.write("gh %s +100" % sclient.cid)
                            return True
                        else:
                            valor = "2000" ######### PRECIO
                            valor2 = 2000  ######### PRECIO
                            nombre = 'Health'  ######### NOMBRE ARMA
                            if (valor2 > dinero):
                                if(idioma == "EN"):
                                    client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                                elif(idioma == "ES"):
                                    client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                                elif(idioma == "FR"):
                                    client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                                elif(idioma == "DE"):
                                    client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                                return False
                            else:
                                q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
                                self.console.storage.query(q)
                                self.console.write("gh %s +100" % sclient.cid)
                                sobran=dinero-valor2
                                if(idioma == "ES"):
                                    client.message('^7Has Comprado ^2%s ^7a %s. Te Quedan:^2%s ^7coins' % (nombre,sclient.exactName,sobran))
                                else:
                                    client.message('^7You have Bought ^2%s^7 to %s. You have:^2%s ^7coins' % (nombre,sclient.exactName,sobran))
                                return True
                else:
                    if(client.maxLevel >= 100):
                        self.console.write("gh %s +100" % client.cid)
                        return True
                    else:
                        valor = "2000" ######### PRECIO
                        valor2 = 2000  ######### PRECIO
                        nombre = 'Health'  ######### NOMBRE ARMA
                        if (valor2 > dinero):
                            if(idioma == "EN"):
                                client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                            elif(idioma == "ES"):
                                client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                            elif(idioma == "FR"):
                                client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                            elif(idioma == "DE"):
                                client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                            return False
                        else:
                            q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (valor,client.id))
                            self.console.storage.query(q)
                            self.console.write("gh %s +100" % client.cid)
                            sobran=dinero-valor2
                            if(idioma == "ES"):
                                client.message('^7Has Comprado ^2%s ^7Te Quedan:^2%s ^7coins' % (nombre,sobran))
                            else:
                                client.message('^7You have Bought ^2%s ^7You have:^2%s ^7coins' % (nombre,sobran))
                            return True
            else:
            	if(idioma == "EN"):
                    client.message("Couldn't find: ^2%s" % input[0])
                elif(idioma == "ES"):
                    client.message("No se encontro: ^2%s" % input[0])
                elif(idioma == "FR"):
                    client.message("In French: Couldn't find: ''^2%s" % input[0])
                elif(idioma == "DE"):
                    client.message("In German: Couldn't find: ^2%s" % input[0])
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
                            weapon.insert( 1, 'Sr8')
                        if 'D' in azul:
                            weapon.insert( 1, 'Spas')
                        if 'E' in azul:
                            weapon.insert( 1, 'MP5K')
                        if 'F' in azul:
                            weapon.insert( 1, 'UMP45')
                        if 'G' in azul:
                            weapon.insert( 1, 'HK69')
                        if 'H' in azul:
                            weapon.insert( 1, 'LR300')
                        if 'I' in azul:
                            weapon.insert( 1, 'G36')
                        if 'J' in azul:
                            weapon.insert( 1, 'PSG1')
                        if 'O' in azul:
                            weapon.insert( 1, 'AK103')
                        if 'Q' in azul:
                            weapon.insert( 1, 'Negev')
                        if 'S' in azul:
                            weapon.insert( 1, 'M4A1')
                        if(dinero > precio_azul):
                            q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (precio_azul,c.id))
                            self.console.storage.query(q)
                            self.console.write("gw %s %s" % (c.cid,azul))
                            c.message('You are autobuying: ^2%s' % ('^7, ^2'.join(weapon)))
                        else:
                            if(idioma == "EN"):
                                client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                            elif(idioma == "ES"):
                                client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                            elif(idioma == "FR"):
                                client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                            elif(idioma == "DE"):
                                client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                            return False
            if(c.team == b3.TEAM_RED):
                q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (c.id))
                cursor = self.console.storage.query(q)
                r = cursor.getRow()
                rojo = r['rojo']
                dinero = r['dinero']
                precio_rojo = r['precio_rojo']
                idioma = r['idioma']
                if(c.maxLevel >= 100):
                    self.console.write("gw %s %s" % (c.cid,rojo))
                else:
                    if rojo:
                        weapon = []
                        if 'K' in rojo:
                            weapon.insert( 1, 'HE Nade')
                        if 'L' in rojo:
                            weapon.insert( 1, 'Flash Nade')
                        if 'M' in rojo:
                            weapon.insert( 1, 'Smoke Nade')
                        if 'A' in rojo:
                            weapon.insert( 1, 'Kevlar')
                        if 'B' in rojo:
                            weapon.insert( 1, 'TacGoggles')
                        if 'C' in rojo:
                            weapon.insert( 1, 'MedKit')
                        if 'F' in rojo:
                            weapon.insert( 1, 'Helmet')
                        if(dinero > precio_rojo):
                            q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (precio_rojo,c.id))
                            self.console.storage.query(q)
                            self.console.write("gw %s %s" % (c.cid,rojo))
                            c.message('You are autobuying: ^2%s' % ('^7, ^2'.join(weapon)))
                        else:
                            if(idioma == "EN"):
                                client.message("You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                            elif(idioma == "ES"):
                                client.message('^1No tienes ^7suficiente dinero. Tienes: ^2%s ^7Coins' % dinero)
                            elif(idioma == "FR"):
                                client.message("In French: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                            elif(idioma == "DE"):
                                client.message("In German: You ^1don't have ^7enough coins. You have: ^2%s ^7Coins" % dinero)
                            return False
                        