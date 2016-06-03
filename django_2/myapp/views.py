from django.shortcuts import render

# Create your views here.
 
from django.template import Context, loader
from django.http import HttpResponse,HttpResponseRedirect
from django.db import connection
from collections import namedtuple
from django.shortcuts import render_to_response 
from django.template import RequestContext
from django.contrib import auth
from myapp.forms import priceForm,orderForm,MyRegistrationForm
from django.http import Http404
from django.core.context_processors import csrf
from math import *
def index(request,form_error=0):
	tmpl=loader.get_template("index.html")
	registration_form=MyRegistrationForm()
	if form_error==0:
		form=priceForm()
	else:
		form=priceForm(request.POST)
	if form_error==0 and request.method=='POST':
		if "registerButton" in request.POST:
			registration_form=MyRegistrationForm(request.POST)
			if registration_form.is_valid():
				registration_form.save()
				registration_form=MyRegistrationForm()
	c=connection.cursor()
	
	qq="select DISTINCT f.food_name from food f , menu m where f.food_id=m.food_id ORDER BY F.food_name";
	c.execute(qq)
	food_list=[]
	for ii in c.fetchall():
		food_list.append(ii[0])

	qq="SELECT DISTINCT CATEGORY FROM FOOD order by CATEGORY"
	c.execute(qq)
	categories=c.fetchall()

	cont=RequestContext(request, {'registration_form':registration_form,
		'form':form,'categories':categories})
	
	return HttpResponse(tmpl.render(cont))

def show_food_category(request,category_name,pagination=1):
	registration_form=MyRegistrationForm()
	if request.method=='POST':
		if "registerButton" in request.POST:
			registration_form=MyRegistrationForm(request.POST)
			print('here')
			if registration_form.is_valid():
				registration_form.save()
				registration_form=MyRegistrationForm()

	c=connection.cursor()
	#print(category_name)
	c.execute("SELECT M.BRANCH_ID,F.food_name,M.PRICE,find_rating(m.menu_id),M.menu_id,M.amount FROM FOOD F, MENU M \
	WHERE F.FOOD_ID=M.FOOD_ID AND F.CATEGORY=%s order by m.price",(category_name,))
	
	info=c.fetchall()
	foods=[]
	for ii in info:
		foods.append([])

	i=0
	cnt=0
	pagination=int (pagination)
	pagination_num=len(info)/9
	start=9*(pagination-1)
	end=start+9
	info=info[start:end]
	for ii in info:
		c.execute("select r.restaurant_name,b.ADDRESS from restaurant r , branch b \
			where r.restaurant_id=b.restaurant_id and b.branch_id=%s",(ii[0],))
		temp=c.fetchone()

		foods[i].append(ii[0])
		foods[i].append(ii[1])
		foods[i].append(ii[2])
		foods[i].append(ii[3])
		foods[i].append(temp[0])
		foods[i].append(temp[1])
		foods[i].append(ii[4])
		foods[i].append(ii[5])
		i+=1
	
	qq="select DISTINCT f.food_name from food f , menu m where f.food_id=m.food_id ORDER BY F.food_name";
	c.execute(qq)
	food_list=[]
	for ii in c.fetchall():
		food_list.append(ii[0])

	
	pagination_num=int(ceil(pagination_num))
	pagination_list=[]
	if pagination>2:
		pagination_list.append(pagination-2)
	if pagination>1:
		pagination_list.append(pagination-1)
	pagination_list.append(pagination)
	if pagination+1<=pagination_num:
		pagination_list.append(pagination+1)
	if pagination+2<=pagination_num:
		pagination_list.append(pagination+2)
	return render(request,"food_category.html",{'registration_form':registration_form,'pagination_num':pagination_num,'pagination':pagination,
		'pagination_list':pagination_list,'food_list':food_list,'foods':foods,
		'category_name':category_name})
def all_restaurants(request,pagination=1):
	#print("all restaurants")

	c=connection.cursor()
	c.execute("select * from restaurant order by restaurant_name")
	restaurant_list=c.fetchall()
	qq="select AREA_NAME from AREA"
	c.execute(qq)

	area_list=[]
	for ii in c.fetchall():
		#print(ii[0])
		area_list.append(ii[0])
	form=priceForm()
	categories=[]
	c.execute("select DISTINCT category from Food")
	categories=c.fetchall()
	qq="select DISTINCT f.food_name from food f , menu m where f.food_id=m.food_id ORDER BY F.food_name";
	c.execute(qq)
	food_list=[]
	for ii in c.fetchall():
		food_list.append(ii[0])
	return render_to_response('all_restaurants.html',RequestContext(request,{'food_list':food_list,
		'categories':categories,'restaurants':restaurant_list,'area_list':area_list,'form':form}))
def show_restaurants(request,area,form_error=0,pagination=1): 
	registration_form=MyRegistrationForm()
	if request.method=='POST':
		if "registerButton" in request.POST:
			registration_form=MyRegistrationForm(request.POST)
			if registration_form.is_valid():
				registration_form.save()
				registration_form=MyRegistrationForm()
	area=area.lower()
	c=connection.cursor()
	c.execute("SELECT B.branch_id,B.restaurant_id FROM AREA A,BRANCH B \
		WHERE A.AREA_ID=B.AREA_ID AND lower(A.AREA_NAME)=%s",(area,))
	branches=c.fetchall()
	
	if len(branches)==0:
		return index(request)
	
	categories=[]
	for branch in branches:
		c.execute("select F.category from Menu M,Food F where M.food_id=F.food_id and M.branch_id=%s",(branch[0],))
		for ii in c.fetchall():
			categories.append(ii)
	
	categories=list(set(categories))	
	restaurant_list=[]
	contact_list=[]
	i=0
	for branch in branches:
		restaurant_list.append([])

	for branch in branches:
		c.execute("select restaurant_name from restaurant where restaurant_id=%s",(branch[1],))
		temp=c.fetchone()
		c.execute("select phone from contact_branch where branch_id=%s",(branch[0],))
		
		temp1=c.fetchall()
		a=''
		cnt=0
		for number in temp1:
			if a!='':
				a=a+','
			a=a+str(number[0])
			cnt+=1
			if cnt==4:
				a+="\n"
				cnt=0	
			
		#print(a)
		restaurant_list[i].append(branch[0])
		restaurant_list[i].append(temp[0])
		restaurant_list[i].append(a)
		i+=1
	if form_error==0:
		form=priceForm()
	else:
		form=priceForm(request.POST)
	qq="select DISTINCT f.food_name from food f , menu m where f.food_id=m.food_id ORDER BY F.food_name";
	c.execute(qq)
	food_list=[]
	for ii in c.fetchall():
		food_list.append(ii[0])
	return render_to_response("restaurants.html",RequestContext(request,{'registration_form':registration_form,
		'area_name':area,'food_list':food_list,'form':form,'restaurants':restaurant_list,'area':area,
		'user':request.user,'categories':categories}))
def area_price_category(request,area):
	if request.method=='POST':
		form=priceForm(request.POST)
		if form.is_valid():
			price1=form.cleaned_data['price1']
			price2=form.cleaned_data['price2']
			c=connection.cursor()
			c.execute("select b.branch_id,(select restaurant_name from restaurant where restaurant_id=b.restaurant_id),\
			b.address from Area a, Branch b where a.AREA_ID=b.AREA_ID and lower(a.AREA_NAME)=%s",(area.lower(),))
		
			branches=c.fetchall()

			foods=[]
			for branch in branches:
				for i in range (1,50):
					foods.append([])
			
			i=0
			for branch in branches:
				c.execute("select F.food_name,F.category,M.price,find_rating(m.menu_id),M.menu_id from Menu M, Food F\
				 where M.food_id=F.food_id and M.branch_id=%s and M.price>=%s and M.price<=%s \
				 order by m.price",(branch[0],price1,price2,))
			
				temp=c.fetchall()
				for ii in temp:
					foods[i].append(branch[0])
					foods[i].append(ii[0])
					foods[i].append(ii[2])
					foods[i].append(ii[3])
					foods[i].append(branch[1])
					foods[i].append(branch[2])
					foods[i].append(ii[4])
				i+=1
			return render(request,"food_category.html",{'foods':foods,'price1':price1,'price2':price2})
		else :
			return show_restaurants(request,area,1)
	return show_restaurants(request,area,1)
def area_food_category(request,area,category_name):
	c=connection.cursor()
	c.execute("select b.branch_id,(select restaurant_name from restaurant where restaurant_id=b.restaurant_id),\
	b.address from Area a, Branch b where a.AREA_ID=b.AREA_ID and lower(a.AREA_NAME)=lower(%s)",(area,))
	branches=c.fetchall()
	foods=[]
	for branch in branches:
		for i in range (1,50):
			foods.append([])
	
	i=0

	for branch in branches:
		c.execute("select F.food_name,F.category,M.price,find_rating(m.menu_id),M.menu_id from Menu M, Food F\
		 where M.food_id=F.food_id and M.branch_id=%s and lower(F.category)=lower(%s) \
		 order by m.price",(branch[0],category_name,))
	
		temp=c.fetchall()
		for ii in temp:
			foods[i].append(branch[0])
			foods[i].append(ii[0])
			foods[i].append(ii[2])
			foods[i].append(ii[3])
			foods[i].append(branch[1])
			foods[i].append(branch[2])
			foods[i].append(ii[4])
		i+=1
	return render(request,"food_category.html",{'foods':foods,'category_name':category_name})
def show_menu(request,branch_id,sort_rating=0,pagination=1,form_error=0):
	registration_form=MyRegistrationForm()
	form=priceForm()
	if form_error!=0:
		form=priceForm(request.POST)

	if request.method=='POST':
		if "registerButton" in request.POST:
			registration_form=MyRegistrationForm(request.POST)
			print('here')
			if registration_form.is_valid():
				registration_form.save()
				registration_form=MyRegistrationForm()
	c=connection.cursor()
	if sort_rating==1:
		c.execute("SELECT F.category,F.food_name,M.PRICE,find_rating(m.menu_id),M.menu_id,M.amount FROM FOOD F, MENU M \
		WHERE F.FOOD_ID=M.FOOD_ID AND M.branch_id=%s  order by find_rating(m.menu_id)",(branch_id,))
	else:
		c.execute("SELECT F.category,F.food_name,M.PRICE,find_rating(m.menu_id),M.menu_id,M.amount FROM FOOD F, MENU M \
		WHERE F.FOOD_ID=M.FOOD_ID AND M.branch_id=%s order by m.price",(branch_id,))
	#
	
	info=c.fetchall()
	foods=[]
	for ii in info:
		foods.append([])
	i=0
	for ii in info:
		c.execute("select r.restaurant_name,b.ADDRESS from restaurant r , branch b \
			where r.restaurant_id=b.restaurant_id and b.branch_id=%s",(branch_id,))
		temp=c.fetchone()

		foods[i].append(ii[1]) #food name
		foods[i].append(ii[0]) #category
		foods[i].append(ii[2]) #price
		foods[i].append(ii[4]) #menu id
		foods[i].append(ii[3]) #rating
		foods[i].append(ii[5]) #amount
		foods[i].append(temp[0]) #res name
		foods[i].append(temp[1]) #res addres
		i+=1
	
	c.execute("select r.restaurant_name,b.address from branch b,restaurant r where b.branch_id=%s and \
		b.restaurant_id=r.restaurant_id",(branch_id,))
	temp=c.fetchone()
	restaurant_name=temp[0]
	res_address=temp[1]
	c.execute("SELECT DISTINCT CATEGORY FROM FOOD F, Menu M where F.food_id=M.food_id and M.branch_id=%s\
	 order by CATEGORY",(branch_id,))
	categories=c.fetchall()
	return render(request,"menu.html",RequestContext(request,{'form':form,
		'foods':foods,'have_name':restaurant_name,'have_address':res_address,'user':request.user,
		'branch':branch_id,'categories':categories}))
def branch_price_category(request,branch_id):
	if request.method=='POST':
		form=priceForm(request.POST)
		if form.is_valid():
			c=connection.cursor()
			price1=form.cleaned_data['price1']
			price2=form.cleaned_data['price2']
			c.execute("SELECT F.food_name,M.PRICE,F.category,M.menu_id,find_rating(m.menu_id),M.amount \
			FROM FOOD F, MENU M WHERE F.FOOD_ID=M.FOOD_ID AND M.price>=%s and M.price<=%s \
			AND M.BRANCH_ID=%s order by m.price",(price1,price2,branch_id,))
			
			#c.execute(qq)
			foods=c.fetchall()
			c.execute("select r.restaurant_name,b.address from branch b,restaurant r where b.branch_id=%s \
				and b.restaurant_id=r.restaurant_id",(branch_id,))
			temp=c.fetchone()
			restaurant_name=temp[0]
			res_address=temp[1]
			form=priceForm()
			return render(request,"menu.html",{'form':form,'foods':foods,'user':request.user,
				'branch':branch_id,'have_name':restaurant_name,'have_address':res_address,
				'price1':price1,'price2':price2})
		
		return show_menu(request,branch_id,1,1,1)
	return show_menu(request,branch_id,1)
def branch_food_category(request,branch_id,category_name):
	c=connection.cursor()
	c.execute("select f.food_name,f.category,m.price,m.menu_id,find_rating(m.menu_id),m.amount from Food f,Menu m\
	 where f.food_id=m.food_id and m.branch_id=%s and f.category=%s order by m.price",(branch_id,category_name,))
	
	foods=c.fetchall()
	c.execute("select r.restaurant_name,b.address from branch b, restaurant r where b.restaurant_id=r.restaurant_id \
		and b.branch_id=%s",(branch_id,))
	temp=c.fetchone()
	restaurant_name=temp[0]
	res_address=temp[1]
	c.execute("SELECT DISTINCT CATEGORY FROM FOOD F, Menu M where F.food_id=M.food_id and M.branch_id=%s\
	 order by CATEGORY",(branch_id,))
	categories=c.fetchall()

	return render(request,"menu.html",{'categories':categories,'foods':foods,'user':request.user,'branch':branch_id,
		'have_name':restaurant_name,'have_address':res_address,'category_name':category_name})

def show_food_category_with_name(request,food_name,category_name,pagination=1):
	registration_form=MyRegistrationForm()
	if request.method=='POST':
		if "registerButton" in request.POST:
			registration_form=MyRegistrationForm(request.POST)
			print('here')
			if registration_form.is_valid():
				registration_form.save()
				registration_form=MyRegistrationForm()

	c=connection.cursor()
	#print(category_name)
	temp="%"+food_name.lower()+"%"
	c.execute("SELECT M.BRANCH_ID,F.food_name,M.PRICE,find_rating(m.menu_id),M.menu_id,M.amount FROM FOOD F, MENU M \
	WHERE F.FOOD_ID=M.FOOD_ID AND F.CATEGORY=%s and lower(f.food_name) like %s order by m.price",(category_name,temp,))
	
	info=c.fetchall()
	foods=[]
	for ii in info:
		foods.append([])

	i=0
	cnt=0
	pagination=int (pagination)
	pagination_num=len(info)/9
	start=9*(pagination-1)
	end=start+9
	info=info[start:end]
	for ii in info:
		c.execute("select r.restaurant_name,b.ADDRESS from restaurant r , branch b \
			where r.restaurant_id=b.restaurant_id and b.branch_id=%s",(ii[0],))
		temp=c.fetchone()

		foods[i].append(ii[0])
		foods[i].append(ii[1])
		foods[i].append(ii[2])
		foods[i].append(ii[3])
		foods[i].append(temp[0])
		foods[i].append(temp[1])
		foods[i].append(ii[4])
		foods[i].append(ii[5])
		i+=1
	
	qq="select DISTINCT f.food_name from food f , menu m where f.food_id=m.food_id ORDER BY F.food_name";
	c.execute(qq)
	food_list=[]
	for ii in c.fetchall():
		food_list.append(ii[0])

	
	pagination_num=int(ceil(pagination_num))
	pagination_list=[]
	if pagination>2:
		pagination_list.append(pagination-2)
	if pagination>1:
		pagination_list.append(pagination-1)
	pagination_list.append(pagination)
	if pagination+1<=pagination_num:
		pagination_list.append(pagination+1)
	if pagination+2<=pagination_num:
		pagination_list.append(pagination+2)
	return render(request,"food_category.html",{'registration_form':registration_form,'pagination_num':pagination_num,'pagination':pagination,
		'pagination_list':pagination_list,'food_list':food_list,'foods':foods,
		'category_name':category_name,'food_name':food_name})
def search_food(request,food="",pagination=1):
	registration_form=MyRegistrationForm()
	food_name=""
	if request.method=='POST':
		if "registerButton" in request.POST:
			registration_form=MyRegistrationForm(request.POST)
			if registration_form.is_valid():
				registration_form.save()
				registration_form=MyRegistrationForm()
			food_name=food
		else:
			food_name=request.POST['search_food']
	
	else:
		food_name=food
	c=connection.cursor()
	temp="%"+food_name.lower()+"%"
	c.execute("select F.food_name,F.category,M.price,M.menu_id,find_rating(m.menu_id),\
		M.amount,M.branch_id from food F , menu M where f.food_id=m.food_id \
		and lower(f.food_name) like %s order by m.price",(temp,))

	foods=c.fetchall()

	pagination=int(pagination)
	pagination_num=len(foods)/9
	start=9*(pagination-1)
	end=start+9
	foods=foods[start:end]

	foodlist=[]
	i=0
	for ii in foods:
		foodlist.append([])

	for ii in foods:
		#qq="select r.restaurant_name,b.address from restaurant r , branch b where r.restaurant_id=b.restaurant_id and b.branch_id={0}".format(ii[6])
		c.execute("select r.restaurant_name,b.address from restaurant r ,\
		 branch b where r.restaurant_id=b.restaurant_id and b.branch_id=%s",(ii[6],))
		temp=c.fetchone()
		foodlist[i].append(ii[0])
		foodlist[i].append(ii[1])
		foodlist[i].append(ii[2])
		foodlist[i].append(ii[3])
		foodlist[i].append(ii[4])
		foodlist[i].append(ii[5])
		foodlist[i].append(temp[0])
		foodlist[i].append(temp[1])
		i+=1
	foodsearch=1

	qq="select DISTINCT f.food_name from food f , menu m where f.food_id=m.food_id ORDER BY F.food_name";
	c.execute(qq)
	food_list=[]
	for ii in c.fetchall():
		food_list.append(ii[0])
	temp="%"+food_name.lower()+"%"
	c.execute("SELECT DISTINCT CATEGORY FROM FOOD F, Menu M where F.food_id=M.food_id and lower(F.food_name) like %s\
	 order by CATEGORY",(temp,))
	categories=c.fetchall()
	print(categories)
	pagination_num=int(ceil(pagination_num))
	
	pagination_list=[]
	if pagination>2:
		pagination_list.append(pagination-2)
	if pagination>1:
		pagination_list.append(pagination-1)
	pagination_list.append(pagination)
	if pagination+1<=pagination_num:
		pagination_list.append(pagination+1)
	if pagination+2<=pagination_num:
		pagination_list.append(pagination+2)
	return render(request,"menu.html",RequestContext(request,{'registration_form':registration_form,
		'pagination_num':pagination_num,'pagination':pagination,'pagination_list':pagination_list,
		'search_name':food_name,'food_list':food_list,'foods':foodlist,'user':request.user,
		'food_search':foodsearch,'categories':categories}))
def show_branches(request,restaurant_id,pagination=1):
	#qq="SELECT DISTINCT CATEGORY FROM FOOD"
	c=connection.cursor()
	#c.execute(qq)
	#categories=c.fetchall()

	#print(restaurant_id)
	categories=[]
	c.execute("select restaurant_name from restaurant where restaurant_id=%s",(restaurant_id,))
	restaurant_name=c.fetchone()

	c.execute("select (select AREA_NAME from Area where AREA_ID=b.AREA_ID),b.ADDRESS,b.branch_id\
	 from restaurant r , branch b where b.restaurant_id=r.restaurant_id and r.restaurant_id=%s",(restaurant_id,))
	branches=c.fetchall()

	restaurant_list=[]
	for branch in branches:
		c.execute("select f.category from food f,menu m where \
			f.food_id=m.food_id and m.branch_id=%s",(branch[2],))
		
		temp=c.fetchall()
		for ii in temp:
			categories.append(ii)
	categories=list(set(categories))
	for branch in branches:
		restaurant_list.append([])
	i=0

	for branch in branches:
		c.execute("select phone from contact_branch where branch_id=%s",(branch[2],))
		temp1=c.fetchall()
		a=''
		for number in temp1:
			if a!='':
				a=a+','
			a=a+str(number[0])

		restaurant_list[i].append(branch[0])
		restaurant_list[i].append(branch[1])
		restaurant_list[i].append(branch[2])
		restaurant_list[i].append(a)
		i+=1
	qq="select DISTINCT f.food_name from food f , menu m where f.food_id=m.food_id ORDER BY F.food_name";
	c.execute(qq)
	food_list=[]
	for ii in c.fetchall():
		food_list.append(ii[0])
	return render_to_response("branch.html",RequestContext(request,{'food_list':food_list,'user':request.user,
		'restaurant_list':restaurant_list,'restaurant_name':restaurant_name[0],'categories':categories}))
def price_category(request,price1=0,price2=0,pagination=1):
	registration_form=MyRegistrationForm()
	if request.method=='POST':
		if "registerButton" in request.POST:
			registration_form=MyRegistrationForm(request.POST)
			if registration_form.is_valid():
				registration_form.save()
				registration_form=MyRegistrationForm()
		else:
			form=priceForm(request.POST)
			if form.is_valid():
				price1=form.cleaned_data['price1']
				price2=form.cleaned_data['price2']
				c=connection.cursor()
				c.execute("SELECT M.BRANCH_ID,F.food_name,M.PRICE,find_rating(m.menu_id),M.menu_id,M.amount\
				FROM FOOD F, MENU M WHERE F.FOOD_ID=M.FOOD_ID AND M.price>=%s and M.price<=%s\
				 order by m.price",(price1,price2,))
				info=c.fetchall()


				i=0

				pagination=int (pagination)
				pagination_num=len(info)/9
				start=9*(pagination-1)
				end=start+9
				info=info[start:end]
				pagination_num=int(ceil(pagination_num))
				pagination_list=[]
				if pagination>2:
					pagination_list.append(pagination-2)
				if pagination>1:
					pagination_list.append(pagination-1)
				pagination_list.append(pagination)
				if pagination+1<=pagination_num:
					pagination_list.append(pagination+1)
				if pagination+2<=pagination_num:
					pagination_list.append(pagination+2)

				foods=[]
				for ii in info:
					foods.append([])
				for ii in info:
					c.execute("select r.restaurant_name,b.ADDRESS from restaurant r , branch b\
					 where r.restaurant_id=b.restaurant_id and b.branch_id=%s",(ii[0],))
					temp=c.fetchone()

					foods[i].append(ii[0])
					foods[i].append(ii[1])
					foods[i].append(ii[2])
					foods[i].append(ii[3])
					foods[i].append(temp[0])
					foods[i].append(temp[1])
					foods[i].append(ii[4])
					foods[i].append(ii[5])
					i+=1
				category_name=''	
				return render(request,"food_category.html",{'registration_form':registration_form,
					'foods':foods,'price1':price1,'price2':price2,'pagination_num':pagination_num,
					'pagination':pagination,'pagination_list':pagination_list})
			args={}
			args.update(csrf(request))
			args['form']=form
			return index(request,1)
	
	if price1!=0 and price2!=0:
		registration_form=MyRegistrationForm()
		c=connection.cursor()
		c.execute("SELECT M.BRANCH_ID,F.food_name,M.PRICE,find_rating(m.menu_id),M.menu_id,M.amount\
		FROM FOOD F, MENU M WHERE F.FOOD_ID=M.FOOD_ID AND M.price>=%s and M.price<=%s\
		 order by m.price",(price1,price2,))
		info=c.fetchall()

		i=0
		pagination=int (pagination)
		pagination_num=len(info)/9
		start=9*(pagination-1)
		end=start+9
		info=info[start:end]
		pagination_num=int(ceil(pagination_num))
		pagination_list=[]
		if pagination>2:
			pagination_list.append(pagination-2)
		if pagination>1:
			pagination_list.append(pagination-1)
		pagination_list.append(pagination)
		if pagination+1<=pagination_num:
			pagination_list.append(pagination+1)
		if pagination+2<=pagination_num:
			pagination_list.append(pagination+2)

		foods=[]
		for ii in info:
			foods.append([])
		for ii in info:
			c.execute("select r.restaurant_name,b.ADDRESS from restaurant r , branch b\
			 where r.restaurant_id=b.restaurant_id and b.branch_id=%s",(ii[0],))
			temp=c.fetchone()

			foods[i].append(ii[0]) #branch
			foods[i].append(ii[1]) #name
			foods[i].append(ii[2]) 
			foods[i].append(ii[3])
			foods[i].append(temp[0])
			foods[i].append(temp[1])
			foods[i].append(ii[4])
			foods[i].append(ii[5])
			i+=1
		category_name=''	
		return render(request,"food_category.html",{'registration_form':registration_form,
			'foods':foods,'price1':price1,'price2':price2,'pagination_num':pagination_num,
			'pagination':pagination,'pagination_list':pagination_list})
	return index(request,1)
def order_submit(request,order_id,area_id='NULL',address='NULL'):
	orderinfo_list=request.POST.getlist('checks[]')
	#print("check list")
	print(orderinfo_list)
	temp2=[]
	order_list=[]
	c=connection.cursor()
	print(address)
	for ii in orderinfo_list:
		c.execute("update order_info set is_checked=1 where orderinfo_id={0}".format(ii))
		
	c.execute("update foodorder set is_submitted=1,area_id=%s,address=%s,\
		order_date=sysdate,status=0 where order_id=%s",(area_id,address,order_id,))

	for ii in orderinfo_list:
		c.execute("select menu_id,amount from order_info where orderinfo_id=%s",(ii,))
		#c.execute(qq)
		temp3=c.fetchone()
		temp2.append(temp3)

	for ii in temp2:
		order_list.append([])
	i=0
	total=0
	bb=set()
	for ii in temp2:
		c.execute("select food_id, branch_id,price from menu where menu_id=%s",(ii[0],))
		
		temp3=c.fetchone()
		#print(temp3[2])
		order_list[i].append(ii[1]) #amount
		order_list[i].append(temp3[2]) #price
		total+=(temp3[2]*ii[1])
		#i+=1
		#c.execute("update menu set amount=amount-%s where menu_id=%s",(ii[1],ii[0],))
		#c.execute("commit;")
		c.execute("select food_name, category from food where food_id=%s",(temp3[0],))
		#c.execute(qq)
		temp4=c.fetchone()
		order_list[i].append(temp4[0])#food name
		order_list[i].append(temp4[1])#category
		#i+=1
		print(temp4[0])
		c.execute("select b.address, b.dcharge,r.restaurant_name from branch b, restaurant r\
		 where b.restaurant_id=r.restaurant_id and b.branch_id=%s",(temp3[1],))
		
		temp5=c.fetchone()
		order_list[i].append(temp5[0]) #restaurant address
		order_list[i].append(temp5[1])# charge
		order_list[i].append(temp5[2])#restaurant name
		if temp3[1] not in bb:
			total+=temp5[1]
			bb.add(temp3[1])

		i+=1

	c.callproc("update_bill",(request.user.username,total))
	return render(request,"order_success.html",RequestContext(request,{'foods':order_list,'total':total}))
def take_order(request):
	c=connection.cursor()
	temp=[]
	name=request.user.username
	print(name)
	order_list=[]
	c.execute("select customer_id from customer where username=%s",(name,))
	
	temp1=c.fetchone()
	print(temp1)
	c.execute("select order_id from foodorder where customer_id=%s and is_submitted=0",(temp1[0],))
	
	temp2=c.fetchone()
	if not temp2:
		raise Http404("You don't have any food in your order List.Please go to menu page and add menu to your list")
	orderid=temp2[0]
	#employee=temp[0]
	c.execute("select menu_id,amount,orderinfo_id from order_info where order_id=%s",(temp2[0],))
	#c.execute(qq)
	temp2=c.fetchall()
	for ii in temp2:
		c.execute("select food_id, branch_id,price from menu where menu_id=%s and amount>=%s",(ii[0],ii[1],))
		#c.execute(qq)
		temp3=c.fetchone()
		if temp3:
			order_list.append([])
	print(order_list)
	if  len(order_list)==0:
		raise Http404("You don't have any food in your order List.Please go to menu page and add menu to your list")
	i=0
	for ii in temp2:
		c.execute("select food_id, branch_id,price from menu where menu_id=%s and amount>=%s",(ii[0],ii[1],))
		#c.execute(qq)
		temp3=c.fetchone()
		if not temp3:
			continue
		order_list[i].append(ii[1]) #amount
		order_list[i].append(temp3[2]) #price
		#i+=1
	
		c.execute("select food_name, category from food where food_id=%s",(temp3[0],))
		
		temp4=c.fetchone()
		order_list[i].append(temp4[0])#food name
		order_list[i].append(temp4[1])#category
		#i+=1

		c.execute("select b.address, b.dcharge,r.restaurant_name from branch b, restaurant r\
		 where b.restaurant_id=r.restaurant_id and b.branch_id=%s",(temp3[1],))
		#c.execute(qq)
		temp5=c.fetchone()
		order_list[i].append(temp5[0]) #restaurant address
		order_list[i].append(temp5[1])# charge
		order_list[i].append(temp5[2])#restaurant name
		order_list[i].append(ii[2])#orderinfo_id
		i+=1
	
	print(order_list)
	if request.method=='POST':
		form=orderForm(request.POST)
		if form.is_valid():
			area_id=form.cleaned_data['area']
			address=form.cleaned_data['address']
			print(area_id)
			return order_submit(request,orderid,area_id,address)
			#return render(request,"order_success.html",RequestContext(request,{'order_list':order_list}))
		else:
			return render(request,"order.html",RequestContext(request,{'form':form,'order_list':order_list}))

	form=orderForm();
	return render(request,"order.html",RequestContext(request,{'orderid':orderid,'form':form,'order_list':order_list}))
