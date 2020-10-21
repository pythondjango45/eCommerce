from django.shortcuts import render,redirect
from .models import Contact,User,Product,WishList,Cart,Transaction
from django.core.mail import send_mail
import random
from django.conf import settings
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
# Create your views here.
@csrf_exempt
def validate_username(request):
	
	username = request.POST['username']
	data = {'is_taken': User.objects.filter(email__iexact=username).exists()}
	return JsonResponse(data)
	
def initiate_payment(request):
    
    try:
        user=User.objects.get(email=request.session['email'])
        amount = int(request.POST['amount'])
        
    except:
        return render(request, 'mycart.html', context={'error': 'Wrong Accound Details or amount'})

    transaction = Transaction.objects.create(made_by=user, amount=amount)
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(transaction.made_by.email)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()

    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    return render(request, 'redirect.html', context=paytm_params)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return render(request, 'callback.html', context=received_data)


def index(request):
	return render(request,'index.html')

def seller_index(request):
	return render(request,'seller_index.html')

def contact(request):
	if request.method=="POST":
		cn=request.POST['cname']
		e=request.POST['email']
		m=request.POST['mobile']
		f=request.POST['feedback']
		Contact.objects.create(name=cn,email=e,mobile=m,feedback=f)
		msg="Contact Saved Successfully"
		contacts=Contact.objects.all().order_by('-id')
		return render(request,'contact.html',{'msg':msg,'contacts':contacts})
	else:
		contacts=Contact.objects.all().order_by('-id')
		return render(request,'contact.html',{'contacts':contacts})

def signup(request):
	if request.method=="POST":
		username=request.POST['username']
		if username:
			data={'is_taken':User.objects.filter(email__iexact=username).exists()}
			return JsonResponse(data)
		fn=request.POST['fname']
		ln=request.POST['lname']
		em=request.POST['email']
		mb=request.POST['mobile']
		ps=request.POST['password']
		cps=request.POST['cpassword']
		utype=request.POST['usertype']
		image=request.FILES['image']
		try:
			user=User.objects.get(email=em)
			if user:
				msg="Email Id Already Exists"
				return render(request,'signup.html',{'msg':msg})
		except:
			if ps==cps:
				User.objects.create(fname=fn,lname=ln,email=em,mobile=mb,password=ps,cpassword=cps,usertype=utype,image=image)
				rec=[em,]
				subject="OTP For Successfull Registration"
				otp=random.randint(1000,9999)
				message="Your OTP For Registration Is "+str(otp)
				email_from = settings.EMAIL_HOST_USER
				send_mail(subject, message, email_from, rec)
				return render(request,'enter_otp.html',{'otp':otp,'email':em})
			else:
				msg="Password & Confirm Password Does Not Matched"
				return render(request,'signup.html',{'msg':msg})
	else:
		return render(request,'signup.html')

def login(request):
	if request.method=="POST":
		
		email=request.POST['email']
		password=request.POST['password']
		utype=request.POST['usertype']

		try:
			
			user=User.objects.get(email=email,password=password)
			if user.usertype=="user" and utype=="user":
				if user.status=="active":
					request.session['fname']=user.fname
					request.session['lname']=user.lname
					request.session['email']=user.email
					request.session['image']=user.image.url
					mywishlists=WishList.objects.filter(user=user)
					request.session['len_wishlist']=len(mywishlists)
					mycarts=Cart.objects.filter(user=user)
					request.session['len_cart']=len(mycarts)
					return render(request,'index.html')
				else:
					msg1="Sorry Your Login Status Is Inactive"
					return render(request,'login.html',{'msg':msg})
			
			elif user.usertype=="seller" and utype=="seller":
				if user.status=="active":
					request.session['fname']=user.fname
					request.session['lname']=user.lname
					request.session['email']=user.email
					request.session['image']=user.image.url
					return render(request,'seller_index.html')
				else:
					msg1="Sorry Your Login Status Is Inactive"
					return render(request,'login.html',{'msg1':msg1})

			else:

				msg1="Please select proper Usertype"
				return render(request,'login.html',{'msg1':msg1})

		except Exception as e:
			print(e)

			msg="EMail Or Password Is Incorrect or Status Is Not Inactive"
			return render(request,'login.html',{'msg':msg})
	else:
		return render(request,'login.html')

def verify_otp(request):
	otp=request.POST['otp']
	uotp=request.POST['uotp']
	email=request.POST['email']
	myvar=request.POST['myvar']
	user=User.objects.get(email=email)

	if otp==uotp and myvar=='forgot_password':
		return render(request,'enter_new_password.html',{'email':email})
	elif otp==uotp and myvar=='activate_status':
		user.status="active"
		user.save()
		return render(request,'login.html')
	elif otp==uotp:
		user.status="active"
		user.save()
		msg="Signup Successfully"
		return render(request,'login.html')
	else:
		msg="Incorrect OTP. Please Try Again"
		return render(request,'enter_otp.html',{'otp':otp,'email':email,'msg':msg})

def logout(request):
	try:
		del request.session['fname']
		del request.session['lname']
		del request.session['email']
		del request.session['len_wishlist']
		del request.session['len_cart']
		return render(request,'index.html')
	except:
		return render(request,'index.html')

def forgot_password(request):
	if request.method=="POST":
		print("Hello")
		email=request.POST['email']
		print("Email : ",email)
		user=User.objects.filter(email=email)
		if user:
			rec=[email,]
			subject="OTP For Forgot Password"
			otp=random.randint(1000,9999)
			message="Your OTP For Forgot Password Is "+str(otp)
			email_from = settings.EMAIL_HOST_USER
			send_mail(subject, message, email_from, rec)
			myvar="forgot_password"
			return render(request,'enter_otp.html',{'otp':otp,'email':email,'myvar':myvar})
		else:
			msg="Email Id Does Not Available In Our System"
			return render(request,'forgot_password.html',{'msg':msg})
	else:
		return render(request,'forgot_password.html')

def new_password(request):
	email=request.POST['email']
	npassword=request.POST['npassword']
	cnpassword=request.POST['cnpassword']

	if npassword==cnpassword:
		try:
			user=User.objects.get(email=email)
			user.password=npassword
			user.cpassword=cnpassword
			user.save()
			return render(request,'login.html')
		except:
			pass
	else:
		msg="New Password & Confirm New Password Not Matched"
		return render(request,'enter_new_password.html',{'email':email,'msg':msg})

def change_password(request):
	if request.method=="POST":

		old_password=request.POST['old_password']
		new_password=request.POST['new_password']
		confirm_new_password=request.POST['confirm_new_password']

		try:

			user=User.objects.get(email=request.session['email'])
			if old_password==user.password:
				if new_password==confirm_new_password:
					user.password=new_password
					user.cpassword=new_password
					user.save()
					return redirect('logout')
				else:
					msg="New Password & Confirm New Password Does Not Matched"
					return render(request,'change_password.html',{'msg':msg})
			else:
				msg="Old Password Is incorrect"
				return render(request,'change_password.html',{'msg':msg})

		except:
			pass

	else:
		try:
			user=User.objects.get(email=request.session['email'])
			if user.usertype=="user":
				return render(request,'change_password.html')
			elif user.usertype=="seller":
				return render(request,'seller_change_password.html')
		except:
			pass
def enter_email(request):
	return render(request,'enter_email.html')

def activate_status(request):
	email=request.POST['email']

	try:
		user=User.objects.get(email=email)
		if user:
			rec=[email,]
			subject="OTP For Forgot Password"
			otp=random.randint(1000,9999)
			message="Your OTP For Forgot Password Is "+str(otp)
			email_from = settings.EMAIL_HOST_USER
			send_mail(subject, message, email_from, rec)
			myvar="activate_status"
			return render(request,'enter_otp.html',{'otp':otp,'email':email,'myvar':myvar})

	except:
		msg="Email Is Not Registered With Us"
		return render(request,'enter_email.html',{'msg':msg})

def add_product(request):
	if request.method=="POST":
		pc=request.POST['product_category']
		pn=request.POST['product_name']
		pp=request.POST['product_price']
		pd=request.POST['product_desc']
		pi=request.FILES['product_image']
		user=User.objects.get(email=request.session['email'])

		Product.objects.create(user=user,product_category=pc,product_name=pn,product_price=pp,product_desc=pd,product_image=pi)
		msg="Product Added Successfully"
		return render(request,'add_product.html',{'msg':msg})
	else:
		return render(request,'add_product.html')

def view_product(request):
	user=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(user=user)
	return render(request,'view_product.html',{'products':products})

def product_detail(request,pk):
	product=Product.objects.get(pk=pk)
	return render(request,'product_detail.html',{'product':product})

def product_unavailable(request,pk):
	product=Product.objects.get(pk=pk)
	if request.method=="POST":
		
		if product.product_stock=='available':
			product.product_stock="unavailable"
		else:
			product.product_stock="available"
		product.save()
		return render(request,'product_detail.html',{'product':product})
	else:
		return render(request,'product_detail.html',{'product':product})

def get_unavailable(request):
	user=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(user=user,product_stock='unavailable')
	return render(request,'unavailable_product.html',{'products':products})

def edit_product(request,pk):
	if request.method=="POST":
		product=Product.objects.get(pk=pk)
		product_name=request.POST['product_name']
		product_price=request.POST['product_price']
		product_desc=request.POST['product_desc']
		try:
			product_image=request.FILES['product_image']
			product.product_name=product_name
			product.product_price=product_price
			product.product_desc=product_desc
			product.product_image=product_image
			product.save()
			return render(request,'product_detail.html',{'product':product})
		except:
			product.product_name=product_name
			product.product_price=product_price
			product.product_desc=product_desc
			product.save()
			return render(request,'product_detail.html',{'product':product})
	else:
		product=Product.objects.get(pk=pk)
		return render(request,'edit_product.html',{'product':product})

def fashion(request):
	if request.method=="POST":
		sortby=request.POST['sortby']
		if sortby=="lowtohigh":
			products=Product.objects.filter(product_category='fashion',product_stock='available').order_by('product_price')
			return render(request,'show_product.html',{'products':products})
		elif sortby=="hightolow":
			products=Product.objects.filter(product_category='fashion',product_stock='available').order_by('-product_price')
			return render(request,'show_product.html',{'products':products})

	products=Product.objects.filter(product_category='fashion',product_stock='available')
	return render(request,'show_product.html',{'products':products})

def electronic(request):
	products=Product.objects.filter(product_category='electronic',product_stock='available')
	return render(request,'show_product.html',{'products':products})

def mobile(request):
	products=Product.objects.filter(product_category='mobile',product_stock='available')
	return render(request,'show_product.html',{'products':products})

def user_product_detail(request,pk):
	flag=True
	flag1=True
	product=Product.objects.get(pk=pk)
	try:
		user=User.objects.get(email=request.session['email'])
		
		mywishlists=WishList.objects.filter(user=user)
		for i in mywishlists:
			if product.pk==i.product.pk:
				flag=False
				break
		mycarts=Cart.objects.filter(user=user)
		for i in mycarts:
			if product.pk==i.product.pk:
				flag1=False
				break
		return render(request,'user_product_detail.html',{'product':product,'flag':flag,'flag1':flag1})
	except:
		return render(request,'user_product_detail.html',{'product':product})

def add_to_wishlist(request,pk):
	flag=True
	user=User.objects.get(email=request.session['email'])
	product=Product.objects.get(pk=pk)
	mywishlists=WishList.objects.filter(user=user)
	
	for i in mywishlists:
		if product.pk==i.product.pk:
			flag=False
			break
	if flag==False:
		msg="Product Is Already In WishList"
		return render(request,'mywishlist.html',{'mywishlists':mywishlists,'msg':msg})
	else:
		mycarts=Cart.objects.filter(user=user,product=product)
		if mycarts:
			msg="This is product is already in Cart So you can not add to Wishlist"
			return redirect('mywishlist')
		else:
			WishList.objects.create(user=user,product=product)
			mywishlists=WishList.objects.filter(user=user)
			request.session['len_wishlist']=len(mywishlists)
			return redirect('mywishlist')

def mywishlist(request):

	user=User.objects.get(email=request.session['email'])
	mywishlists=WishList.objects.filter(user=user)
	request.session['len_wishlist']=len(mywishlists)
	return render(request,'mywishlist.html',{'mywishlists':mywishlists})

def remove_from_wishlist(request,pk):
	user=User.objects.get(email=request.session['email'])
	product=Product.objects.get(pk=pk)
	wishlist=WishList.objects.get(user=user,product=product)
	wishlist.delete()
	mywishlists=WishList.objects.filter(user=user)
	request.session['len_wishlist']=len(mywishlists)
	return render(request,'mywishlist.html',{'mywishlists':mywishlists})

def add_to_cart(request,pk):
	flag=True
	user=User.objects.get(email=request.session['email'])
	product=Product.objects.get(pk=pk)
	mycart=Cart.objects.filter(user=user)
	for i in mycart:
		if product.pk==i.product.pk:
			flag=False
			break
	if flag==False:
		msg="Product Is Already In Cart"
		return render(request,'mycart.html',{'mycart':mycart,'msg':msg})
	else:
		mywishlists=WishList.objects.filter(user=user,product=product)
		if mywishlists:
			msg="This product is already in WishList So you can not add to Cart"
			return redirect('mycart')
		else:
			Cart.objects.create(user=user,product=product)
			mycarts=Cart.objects.filter(user=user)
			request.session['len_cart']=len(mycarts)
			return redirect('mycart')

def mycart(request):
	total_price=0
	user=User.objects.get(email=request.session['email'])
	mycart=Cart.objects.filter(user=user)
	for i in mycart:
		total_price=int(total_price)+int(i.product.product_price)
	print(total_price)
	request.session['len_cart']=len(mycart)
	return render(request,'mycart.html',{'mycart':mycart,'total_price':total_price})

def remove_from_cart(request,pk):
	total_price=0
	user=User.objects.get(email=request.session['email'])
	product=Product.objects.get(pk=pk)
	cart=Cart.objects.get(user=user,product=product)
	cart.delete()
	mycart=Cart.objects.filter(user=user)
	for i in mycart:
		total_price=int(total_price)+int(i.product.product_price)
	request.session['len_cart']=len(mycart)
	return render(request,'mycart.html',{'mycart':mycart,'total_price':total_price})
