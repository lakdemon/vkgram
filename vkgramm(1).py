import vk_api
import time
import sqlite3
from telethon import TelegramClient
from telethon.tl import TLObject
from telethon.tl.functions.account import (
    GetPasswordRequest
)
from telethon.tl.functions.auth import (
    CheckPasswordRequest, LogOutRequest, SendCodeRequest, SignInRequest,
    SignUpRequest, ImportBotAuthorizationRequest
)
from telethon.tl.functions.contacts import (
    GetContactsRequest, ResolveUsernameRequest
)
from telethon.tl.functions.messages import (
    GetDialogsRequest, GetHistoryRequest, ReadHistoryRequest, SendMediaRequest,
    SendMessageRequest
)
from telethon.tl.functions.users import (
    GetUsersRequest
)
from telethon.tl.types import (
    DocumentAttributeAudio, DocumentAttributeFilename,
    InputDocumentFileLocation, InputFileLocation,
    InputMediaUploadedDocument, InputMediaUploadedPhoto, InputPeerEmpty,
    Message, MessageMediaContact, MessageMediaDocument, MessageMediaPhoto,
    InputUserSelf, UserProfilePhoto, ChatPhoto, UpdateMessageID,
    UpdateNewMessage, UpdateShortSentMessage
)
from telethon.utils import find_user_or_chat, get_extension

import curses


def dialogEneting(window,client,subject,opt):
			myscreen.clear()
			myscreen.keypad(False)
			curses.nocbreak()
			myscreen.addstr(curses.LINES-1,0,"Text:")
			text_sending_message = myscreen.getstr(curses.LINES-1,6).decode(encoding="utf-8")
			message_entering = False
			myscreen.clear()
			print(text_sending_message)
			myscreen.keypad(True)
			curses.cbreak()
			if opt == 'vk':
				try:
					client.method('messages.send',{'user_id':subject,'message':text_sending_message})
				except AttributeError:
					print("Всё нормально")
			elif opt == 'tele':
				try:
					client.send_message(subject, text_sending_message)
				except AttributeError:
					print("Всё нормально")
			else:
				print("Unknown option!")
#	




def main():
	#======================================================
	#Авторизация пользователя вк
	api_id = 191328 
	api_hash = '45e5b324d70ec22ed6f1e79afadeeadc'
	#print("Enter your phone for telegram")
	#phone = input()
	phone = '+79531561812'
	#print("Enter your vk login")
	#vk_login = input()
	vk_login = '89531561812'
	#print("Enter your vk pass")
	#vk_pass = input()
	vk_pass = 'lakdemon1996'

	vk = vk_api.VkApi(login=vk_login, password=vk_pass)
	vk.auth()

	client = TelegramClient('lakdemon1', api_id, api_hash)
	if client.connect() != True:
		if client.connect() != True:
			print("CANNOT CONNECT")

	if client.is_user_authorized() != True:
		client.sign_in(phone=phone)
		print("Enter secret code sended on your number")
		tel_code = input()
		me = client.sign_in(code=tel_code)
		myself = client.get_me()
	else:
		print("You are entered to TelegramClient")
		myself = client.get_me()



	r = client(GetDialogsRequest(offset_date=None,offset_id=0,offset_peer=InputPeerEmpty(),limit=20))
	telegram_dialogs=[]
	dialog={}
	print("\n===========================================")
	entity=None

	for i in r.messages:
		try:
			name = None
			for j in r.users:
				if i.to_id.user_id == j.id and j.is_self != True:
					name = j.first_name

			if name == None:
				for j in r.users:
					if i.from_id == j.id:
						name = j.first_name
		except AttributeError:
			try:
				name = None
				for j in r.chats:
					if i.to_id.chat_id == j.id:
						name = j.title
			except AttributeError:
				name = "Some_chanell"
		try:
			#print("From:",name,"\nDate:",i.date,"\nText:",i.message,"\n===========================================")
			if '\n' in i.message:
				dialog = {'name':name,'message':i.message.split('\n')[0][:25],'date':i.date}
			else:
				dialog = {'name':name,'message':i.message[:25],'date':i.date}
		except AttributeError:
			#print("From:",name,"\nDate:",i.date,"\nText: NONE\n===========================================")
			dialog = {'name':name,'message':"None",'date':i.date}
		telegram_dialogs.append(dialog)

	#=========================================================================
	
	friend_list = vk.method('friends.get',{'fields':'nickname','order':'hints'})
	friends_count = friend_list['count']
	friend_list = friend_list['items']
			#В friend_list хранится список друзей, в dialogs_list список диалогов
	dialogs_list = vk.method('messages.getDialogs',{'preview_length':25})
	dialogs_count = dialogs_list['count']
	dialogs_list = dialogs_list['items']
	
	#=========================================================================
	
	#Хитрый прием для получения списка имен пользователей в диалогах
	users_buf = []
	for i in dialogs_list:
		if i['message']['user_id'] > 0:
			users_buf.append(i['message']['user_id'])		
	users_buf = ','.join(map(str,users_buf))
	users_buf = vk.method('users.get',{'user_ids':users_buf})
	
	#=========================================================================
	
	#Составляем список диалогов состояшей только из информации
	# необходимой для отображения и отправки сообщений через интерфейс
	dialogs = []
	for i in dialogs_list:
		current_dialog_keys = i['message'].keys()
		dialog = {}
		is_chat = False
		for j in current_dialog_keys:
			if j == 'chat_id':
				is_chat = True
		if is_chat:
			dialog = {'name':i['message']['title'],'message':i['message']['body'],'date':i['message']['date']}
		elif i['message']['user_id'] < 0: #group
			group_name = vk.method('groups.getById',{'group_id':abs(i['message']['user_id'])})
			dialog = {'name':group_name[0]['name'],'message':i['message']['body'],'date':i['message']['date']}
		else:
			current_dialog_user_name = []
			for j in users_buf:
				if j['id'] == i['message']['user_id']:
					current_dialog_user_name = j['first_name']+" "+j['last_name']
			dialog = {'name':current_dialog_user_name,'message':i['message']['body'],'date':i['message']['date']}
		dialogs.append(dialog)
	
	#=======================================================================
	
	#очищаем список диалогов, теперь мы будем работать со списком dialogs
	users_buf.clear()
	dialogs_list.clear()
	
	#=======================================================================

	#инициализация curses
	#myscreen = curses.initscr() 
	curses.initscr() 
	myscreen = curses.newwin(0,0,0,0)
	curses.cbreak()
	myscreen.keypad(True)

	#=======================================================================

	#переменные для отслеживания манипуляции с интерфейсом
	menu_g = 1  
	menu_v = 1
	list_it = 0

	#=======================================================================

	#основной цикл отрисовки интерфейса
	message_entering=True

	while  menu_g !=0:
		myscreen.border(10)
		myscreen.addstr(0, 4, "          +         ",curses.A_STANDOUT)

# ➔ ➲ ▸       \               
		#try:
		#	myscreen.addstr(0,4,text_sending_message)
	#	except:
		#	pass

		left_menu = [" Контакты "," Сообщения  "," телега "," Музыка "]
		for i in range(4):
			try:
				if menu_v-1 == i:
					myscreen.addstr(i*2+2, 0, left_menu[i],curses.A_STANDOUT)
				else:
					myscreen.addstr(i*2+2, 0, left_menu[i],curses.A_BOLD)
			except:
				pass

		#Вывод меню
		#=======================================================================

		if menu_g == 2 and menu_v == 1:
			for i in range(curses.LINES-5):
				try:
					if list_it == i:
						myscreen.addstr(2+2*i, 15, friend_list[i]['first_name'] +" " + friend_list[i]['last_name'],curses.A_STANDOUT)
					else:
						myscreen.addstr(2+2*i, 15, friend_list[i]['first_name'] +" " + friend_list[i]['last_name'])
				except:
					pass

		if menu_g == 2 and menu_v == 2:
			for i in range(55):
				try:
					if list_it == i:
						myscreen.addstr(2+2*i,15,str(dialogs[i]['name'])+": ",curses.A_STANDOUT)
						myscreen.addstr(2+2*i,17+len(str(dialogs[i]['name'])),dialogs[i]['message'],curses.A_STANDOUT)
					else:
						myscreen.addstr(2+2*i,15,str(dialogs[i]['name'])+": ",curses.A_BOLD)
						myscreen.addstr(2+2*i,17+len(str(dialogs[i]['name'])),dialogs[i]['message'])
				except:
					pass

		if menu_g == 2 and menu_v == 3:
			for i in range(55):
				try:
					if list_it == i:
						myscreen.addstr(2+2*i,15,str(telegram_dialogs[i]['name'])+": "+telegram_dialogs[i]['message'],curses.A_STANDOUT)
					else:
						myscreen.addstr(2+2*i,15,str(telegram_dialogs[i]['name'])+": "+telegram_dialogs[i]['message'])
				except:
					pass
		myscreen.refresh() 
		#myscreen.refresh( 0,0, 0,0, 20,75)
		move=None
		if message_entering==False:
			move = myscreen.getch()
		else:
			myscreen.clear()
			myscreen.keypad(False)
			curses.nocbreak()
			myscreen.addstr(curses.LINES-1,0,"Text:")
			text_sending_message = myscreen.getstr(curses.LINES-1,6).decode(encoding="utf-8")
			message_entering = False
			myscreen.clear()
			print(text_sending_message)
			myscreen.keypad(True)
			curses.cbreak()
#
		if move==curses.KEY_UP:
			if menu_g == 1:
				if menu_v > 1:
					menu_v -= 1
			else:
				list_it-=1
		
		if move==curses.KEY_DOWN:
			if menu_g == 1:
				if menu_v < 4:
					menu_v += 1
			else:
				list_it+=1
		
		if move==curses.KEY_LEFT:
				menu_g -= 1
				list_it = 0
		
		if move==curses.KEY_RIGHT:
			if menu_g < 3:
				menu_g += 1
		myscreen.clear()
 	#конец цикла отрисовки
	#=======================================================================
	
	curses.echo()
	curses.endwin()	
	
	#======================================================================
try:
	main()
except BaseException as e:
	curses.endwin()
	print(e)
finally:	
	print("Good Luck!\n")












































#	for i in r.messages:
#		try:
#			name = None
#			for j in r.users:
#				if i.to_id.user_id == j.id and j.is_self != True:
#					name = j.first_name
#			if name == None:
#				for j in r.users:
#					if i.from_id == j.id:
#						name = j.first_name
#		except AttributeError:
#			try:
#				name = None
#				for j in r.chats:
#					if i.to_id.chat_id == j.id:
#						name = j.title
#			except AttributeError:
#				name = "Some_chanell"
#		try:
#			print("From:",name,"\nDate:",i.date,"\nText:",i.message,"\n===========================================")
#		except AttributeError:
#			print("From:",name,"\nDate:",i.date,"\nText: NONE\n===========================================")
	
	#print("\n\nchats\n",c)
	#for i in c:
	#	print(i)
	#print("\n\nusers\n",u)
	#for i in u:
	#	print(i)
	#asf = GetContactsRequest.GetContacts()
	#print(asf)
	#d=r.dialogs
	#m=r.messages
	#c=r.chats
	#u=r.users
	#for i in r.chats:
	#	print(i,"\n")
	#print(r)
	#print("\n\ndialogs\n")
	#for i in d:
	#	print(i)
	#print(m,"\n\n")
	#print("\n\nmessages\n",m)
	#for i in r.users:
	#	print(i,"\n")






#from_id:10 to_id:666 message:хуй



#
#
#curses.echo()
#curses.endwin()

#If you're not authorized, you need to .sign_in():
#client.send_code_request(phone)
#myself = client.sign_in(phone, input('Enter code: '))
# If .sign_in raises PhoneNumberUnoccupiedError, use .sign_up instead

#time.sleep(5)
#if client.is_user_authorized() == True:
#		send_msg('+79319683581','тест 1','tele')
#		send_msg('133839419','тест 1','vk')
#else:
#	print("client was not authorized")



#print("THIS IS THE END OF PROGRAMM")
#send_msg('@solidshake','а если так','tele')
         
#myscreen = curses.initscr() 
#curses.cbreak()
#myscreen.keypad(True)
#curses.noecho()
#myscreen.border(10) 
#myscreen.addstr(12, 25, "привет",curses.A_STANDOUT) 
#myscreen.refresh() 
#myscreen.getch() 

#menu=curses.KEY_UP

#while menu!=curses.KEY_LEFT:
#    if menu==curses.KEY_UP:
#        myscreen.addstr(12, 25, "привет",curses.A_STANDOUT) 
#    else:
#        myscreen.addstr(12, 25, "привет") 
#    myscreen.refresh() 
#    menu=myscreen.getch() 
#
#
#curses.echo()
#curses.endwin()

#{'id': 388277,
# 'date': 1505668676,
#  'out': 1,
#   'user_id': 44066476,
#    'read_state': 1,
#     'title': '4 всадника сессии',
#      'body': 'пс',
#       'random_id': 937069059,
#        'chat_id': 55,
#         'chat_active': [35600420, 132093044, 133839419, 161285278, 250872852],
#          'push_settings': {'sound': 0, 'disabled_until': 121},
#           'users_count': 6,
#            'admin_id': 250872852,
#             'photo_50': 'https://pp.userapi.com/c637218/v637218419/50e4b/7bcFNJWh9nY.jpg',
#              'photo_100': 'https://pp.userapi.com/c637218/v637218419/50e4a/91w91H7UE4c.jpg',
#               'photo_200': 'https://pp.userapi.com/c637218/v637218419/50e48/ysHZka6twC4.jpg'} 

#conn = sqlite3.connect('AUTH.sqlite')
#cursor = conn.cursor()
#conn.execute('''CREATE TABLE COMPANY
#       (ID      INT PRIMARY KEY ,
#       VK_LOGIN           TEXT  ,
#       VK_PASSW           TEXT  ,
#       TELEGR_NUMBER      TEXT) ;''')
#conn.close()

	#client = TelegramClient('lakdemon1', api_id, api_hash)
	#if client.connect() != True:
	#	if client.connect() != True:
	#		print("CANNOT CONNECT")
	#
	#if client.is_user_authorized() != True:
	#	client.sign_in(phone=phone)
	#	print("Enter secret code sended on your number")
	#	tel_code = input()
	#	me = client.sign_in(code=tel_code)
	#	myself = client.get_me()
	#else:
	#	print("You are entered to TelegramClient")
	#	myself = client.get_me()
	#print(friend_list)
	#print("\n\n\n",friend_list)
	#user_name = vk.method('users.get',{'user_ids':i['message']['user_id']})

	#for i in frined_list:
	#	print(i)
#
#	friend_list = vk.method('friends.get',{'fields':'nickname','order':'hints'})
#	friends_count = friend_list['count']
#	friend_list = friend_list['items']
#
#	dialogs_list = vk.method('messages.getDialogs',{'preview_length':25})
#	dialogs_count = dialogs_list['count']
#	dialogs_list = dialogs_list['items']
#
#	dialogs_users = []
#	dialogs_groups = []
#	dialogs_chats = []
#
#	for i in dialogs_list:
#		try:
#			dialogs_chats.append(i['message']['title'])
#		except KeyError:
#			if i['message']['user_id'] < 0:
#				dialogs_groups.append(abs(i['message']['user_id']))
#			else:
#				dialogs_users.append(i['message']['user_id'])
#	print(dialogs_users)
#
#	dialogs_users_names = vk.method('users.get',{'user_ids':dialogs_users})
