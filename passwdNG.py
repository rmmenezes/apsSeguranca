# -*- coding: utf-8 -*-
import crypt
import string
import random
from random import choice
import datetime
from datetime import date
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import fileinput
import sys

class Psswd:
    def __init__(self):
        print("---")

    # GET shadow's lines users and return a simple list
    def get_file_shadow(self):
        users_shadow = []
        fileShadow = open("/etc/shadow")
        for line in fileShadow:
            users_shadow.append(line)
        return users_shadow

    # GET passwd's lines users and return a simple list
    def get_file_passwd(self):
        users_passwd = []
        filePasswd = open("/etc/passwd")
        for line in filePasswd:
            users_passwd.append(line)
        return users_passwd

    def get_file_group(self):
        groups_info = []
        fileGroupsInfo = open('/etc/group')
        for line in fileGroupsInfo:
            groups_info.append(line)
        fileGroupsInfo.close()
        return groups_info
   
    def get_file_gshadow(self):
        groups_info = []
        fileGroupsInfo = open('/etc/gshadow')
        for line in fileGroupsInfo:
            groups_info.append(line)
        fileGroupsInfo.close()
        return groups_info

    def get_tokens_by_user_shadow(self):
        list_users = self.get_file_shadow()
        list_users_tokens = []
        for users in list_users:
            tokens = []
            tokens = users.split(':')
            list_users_tokens.append(tokens)
        return list_users_tokens

    def get_tokens_by_user_passwd(self):
        list_users = self.get_file_passwd()
        list_users_tokens = []
        for users in list_users:
            tokens = []
            tokens = users.split(':')
            list_users_tokens.append(tokens)
        return list_users_tokens
    
    def get_tokens_by_group_gshadow(self):
        list_groups = self.get_file_gshadow()
        list_groups_token = []
        for groups in list_groups:
            tokens = []
            tokens = groups.split(':')
            list_groups_token.append(tokens)
        return list_groups_token

    def get_tokens_by_group_group(self):
        list_groups = self.get_file_group()
        list_groups_token = []
        for groups in list_groups:
            tokens = []
            tokens = groups.split(':')
            list_groups_token.append(tokens)
        return list_groups_token

    def who_is_the_biggest_ID(self):
        list_tokens = self.get_tokens_by_user_passwd()
        maior = 0
        for user in list_tokens:
            if (int(user[2]) > maior):
                maior = int(user[2])
        return maior

    # Recieve new user data and a date to expire the account, if necessary
    def create_new_user(self, username, password, fullname=None, tellphone=None, email=None, other=None, nivel_access=None, security_question=None, security_asnwer=None,expirationDate =None):
        # Here, we have the line that goint to add in the file shadow

        line_shadow = self.createShadowLineNewUsers(username,password,expirationDate)
    

        # print(line_shadow)
        self.adduser_shadow(line_shadow)

        # Here, we have the line that goint to add in the file passwd
        the_last_biggest_ID = self.who_is_the_biggest_ID() + 1
        # comentarios = '['+ 'fullname:' + str(fullname) + ', tellphone:' + str(tellphone) + ', email:' + str(email) + ', other:' + str(other) + ']'
        comentarios = str(fullname) + "," + str(tellphone) + "," +  str(email) + "," + str(other) 
        line_passwd = username + ':x:' + str(the_last_biggest_ID) + ':' + str(the_last_biggest_ID) + ':' + comentarios + ':/home/' + username + ':/bin/bash'
        # print(line_passwd)
        self.save_passwd(line_passwd)

        # cria um grupo para o novo usuário
        self.createNewGroupUser(username,str(the_last_biggest_ID))

        # cria o diretório home do usuário
        os.system('mkdir /home/' + username)        
        os.system('chown ' +  username + ":" + username + ' /home/' + username )
        


    # cria a linha que deverá ser inserida no arquivo /etc/shadow quando um novo usuário for criado
    def createShadowLineNewUsers(self, user, password,expirationDate = None):

        line_shadow = ''
        
        #--------------------------------------Usuário ---------------------------------------
        line_shadow = user 
        #-------------------------------------------------------------------------------------

        #--------------------------------------Senha -----------------------------------------
        #Cria o salt
        randomsalt = ''.join(random.sample(string.ascii_letters,8))
        randomsalt = '$6$' + randomsalt + '$'
        line_shadow = line_shadow + ":" + crypt.crypt(password, randomsalt)
        #-------------------------------------------------------------------------------------

        #---------------------------- Ultima mudança de senha --------------------------------
        #Data base que o Linux usa 
        baseDate = datetime.date(1970,1,1)
        #Pega o dia atual
        today = date.today()    
        # Calcula a diferença de dias entre o dia de hoje e a data base
        dateLastModPassword = abs((today-baseDate).days)
        # Recebe a data da ultima modficação de senha(neste caso recebe o dia atual)
        line_shadow = line_shadow + ":" + str(dateLastModPassword)
        #-------------------------------------------------------------------------------------

        #-------------------Dias até que a senha possa ser alterada novamente ----------------
        # O padrão é 0
        line_shadow = line_shadow + ":" + str(0)
        #-------------------------------------------------------------------------------------

        #-------------------Dias antes que uma alteração seja necessária ---------------------
        # Caso deseje que o usuário mude a senha após o login, colocar 0
        line_shadow = line_shadow + ":" + str(999999)
        #-------------------------------------------------------------------------------------
        
        #-------------------Dias de avisos antes da expiração da senha -----------------------
        # Caso a senha do usuário tenha data de expiração, define quantos dias antes o usuário
        # será avisado
        line_shadow = line_shadow + ":" + str(7)
        #-------------------------------------------------------------------------------------
        
        #-------------------Dias entre expiração e desativação -------------------------------
        # Os dias em que a conta expirada vai ficar inativa
        line_shadow = line_shadow + ":" 
        #-------------------------------------------------------------------------------------

        #-------------------Data em que a conta vai expirar ----------------------------------
        # Os dias em que a conta expirada vai ficar inativa
        if(expirationDate == None):
            line_shadow = line_shadow + ":" 
        else:
            dateExpiration = abs((expirationDate-baseDate).days)
            line_shadow = line_shadow + ":" + str(dateExpiration)
        

        #-------------------------------------------------------------------------------------

        #-------------------flag especial ----------------------------------------------------
        # Os dias em que a conta expirada vai ficar inativa
        line_shadow = line_shadow + ":\n"  
        #-------------------------------------------------------------------------------------

        return line_shadow

    def createNewGroupUser(self, user, uid):
        # linha nova do /etc/group
        fileLines = self.get_file_group()
        fileLines.append(user + ":x:" + uid +":\n")
        newString_group = ''.join(fileLines)        
        
        # linha nova do /etc/gshadow
        fileLines = self.get_file_gshadow()
        fileLines.append(user + ":!::\n")
        newString_gshadow = ''.join(fileLines)
        
        # print(newString_group)
        # print(newString_gshadow)

        # Escreve no arquivo /etc/group
        fileGroups = open('/etc/group',"w+")
        fileGroups.write(newString_group)
        fileGroups.close()

        # escreve no arquivo /etc/gshadow
        file_gshadow = open('/etc/gshadow',"w+")
        file_gshadow.write(newString_gshadow)
        file_gshadow.close()


    def createPassword(self):
        userName = input('Digite o nome do usuário:')
        userPassword = input("Digite a nova senha:")

        # Starting salt creation
        salt = '$6$'

        # All alphanumeric ascii
        possibleSalt = string.ascii_letters + string.digits

        # Creating salt password
        for a in range(8):
            salt = salt + choice(possibleSalt)
        salt = salt + '$'

        encriptedPassword = crypt.crypt(userPassword, salt)

        user_change = "false"
        # print(encriptedPassword)
        fileShadow = open('/etc/shadow')
        conteudo = fileShadow.readlines()
        fileShadowRead = fileShadow.read().split()
        for line in fileShadowRead:
            lineBreak = line.split(':')
            if(lineBreak[0] == userName):
                print(encriptedPassword)
                lineBreak[1] = encriptedPassword
                print(lineBreak)
                user_change = "true"
                fileShadow.write(makeLineShadow(lineBreak))
                break

        if user_change == "false":
            print("Este usuario não esta presente sistema")

    def makeLineShadow(self, lineBreak):
        new_line = ""
        for i in lineBreak:
            new_line = new_line + i + ":"
        return new_line[:-1]

        # print(len(fileShadowRead))

    def blockUser(self, username):
        tokens = self.get_tokens_by_user_passwd()
        token_change = ''
        for user in tokens:
            if user[0] == username:
                user[1] = '!x'
                token_change = user
                break

        self.update_passwd(user)

    # Atualiza um usuario
    def update_passwd(self, user):
        users_tokens = []
        users_tokens = self.get_tokens_by_user_passwd()
        for i in users_tokens:
            if(i[0] == user[0]):
                users_tokens.remove(i)
                break

        users_tokens.append(user)
        users_tokens_str = ''
        for i in users_tokens:
            users_tokens_str += ':'.join(i)

        fileShadow = open('/etc/passwd', 'w+')
        fileShadow.write(users_tokens_str)

        fileShadow.close()

       # fileShadow = open('/etc/passwd.teste')
        # print(fileShadow.read())

    # salva a galerinha
    def save_passwd(self, user):
        # print(user)
        users_tokens = []
        users_tokens = self.get_tokens_by_user_passwd()
        users_tokens_str = ''
        for i in users_tokens:
            users_tokens_str += ':'.join(i)

        users_tokens_str += user + '\n'
        # fileShadow = open('/etc/passwd', 'w+')
        fileShadow = open('/etc/passwd',"w+")
        fileShadow.write(users_tokens_str)

        fileShadow.close()
        # print(fileShadow.read())

    # return a list of security questions
    def get_listofQuestions(self):
        file = open("questions.txt", "r")
        questions = file.readlines()
        return questions

    # Save a new user on shadow file. Recieves the line to add on /etc/shadow

    def adduser_shadow(self, line):
        file = self.get_file_shadow()
        file.append(line)
        passwd = open('/etc/shadow', 'w+')

        string_to_save = ''.join(file)
        passwd.write(string_to_save)

        passwd.close()
        # print(string_to_save)

    # desbloqueia o usuario
    def unlockUser(self, user):
        users_tokens = []
        users_tokens = self.get_tokens_by_user_passwd()
        for i in users_tokens:
            if i[0] == user:
                i[1] = "x"
                user_unlock = i
                break
        self.update_passwd(user_unlock)
        # print(user_unlock)
        return

    # esta varieavel possui todas as regras de senhas do adm
    rules_pass = []

    # def get_values_of_admin_password():
    def values_pass(self, lower, upper, numero, simbolos, tamSenha):
        self.rules_pass.append(lower)
        self.rules_pass.append(upper)
        self.rules_pass.append(numero)
        self.rules_pass.append(simbolos)
        self.rules_pass.append(tamSenha)

    def get_value_pass(self):
        return self.rules_pass

    def recuperarSenha(self, email):
        alfabeto = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        newPassword = "".join(random.sample(alfabeto,8))

        self.redefinirSenha(self.encontrarUsuarioPorEmail(email), newPassword)

        msg = MIMEMultipart() # Cria instância do objeto de mensagem
        message = " Olá! Sua nova senha para o PasswdNG é: " + newPassword + ".\n Recomendamos que após o login você altere a senha."
         
        # Parâmetros da mensagem
        password = "seguranca"
        msg['From'] = "pwdng2019@gmail.com"
        msg['To'] = email
        msg['Subject'] = "Sua nova senha do PasswdNG"
         
        # Adiciona mensagem ao corpo do e-mail
        msg.attach(MIMEText(message, 'plain'))

        # Cria o server e conecta
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.starttls()
         
        # Credenciais de Login
        server.login(msg['From'], password)
         
        # Envia mensagem ao servidor
        server.sendmail(msg['From'], msg['To'], msg.as_string())
         
        # Fecha conexão com o servidor
        server.quit()

        #print "E-mail enviado com sucesso para %s:" % (msg['To'])

    def encontrarUsuarioPorEmail(self, email):
        file = open('/etc/passwd')
        for i in file.readlines():
            if email in i:
                line = i
        usuario = line.split(':')
        usuario = usuario[0]
        return usuario

    def redefinirSenha(self, usuario, senha):
        self.newPassword = self.encriptPassword(senha)

        file = open('/etc/shadow')
        for i in file.readlines():
            if usuario in i:
                oldPassword = (i[len(usuario)+1 : i.index(':', i.index(':') + 1)])
                i.replace(oldPassword, self.newPassword)

                for line in fileinput.FileInput("/etc/shadow",inplace=1):
                   line = line.replace(oldPassword,self.newPassword)
                   sys.stdout.write(line)

    def encriptPassword(self, senha):
        salt = '$6$'
        possibleSalt = string.ascii_letters + string.digits

        for a in range(8):
            salt = salt + choice(possibleSalt)

        salt = salt + '$'
        encriptedPassword = crypt.crypt(senha,salt)

        return encriptedPassword


if __name__ == "__main__":
    passwdng = Psswd()

    dia = datetime.date(2019,7,18)

    passwdng.create_new_user("7891", "123mudar", "7891", "7891", "7891", "User to study", "1",expirationDate=dia)
    # passwdng.save_shadow2('usersemsenha:*:18089:0:99999:7:::\n')
    # passwdng.unlockUser('teste2')

