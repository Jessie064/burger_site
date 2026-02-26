from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages

from .models import Burger, Feedback, UserProfile, Order, OrderItem
from .forms import RegistrationForm, SecureLoginForm, FeedbackForm, UserProfileForm


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _is_staff(user):
    return user.is_authenticated and user.is_staff


# ---------------------------------------------------------------------------
# Public views
# ---------------------------------------------------------------------------

def home_view(request):
    """Landing page: hero section + featured burgers."""
    featured = Burger.objects.filter(is_available=True)[:3]
    perks = [
        ('🔥', 'Flame-Grilled', 'Char-kissed patties cooked fresh on open flame every time.'),
        ('🥬', 'Fresh Ingredients', 'Locally sourced produce — no preservatives, ever.'),
        ('⚡', 'Fast Service', 'Hot and ready in under 10 minutes, guaranteed.'),
        ('🌍', 'Eco Packaging', '100% compostable wrapping and containers.'),
    ]
    return render(request, 'restaurant/home.html', {'featured': featured, 'perks': perks})


def menu_view(request):
    """Full menu page — all available burgers."""
    burgers = Burger.objects.filter(is_available=True)
    return render(request, 'restaurant/menu.html', {'burgers': burgers})


def contact_view(request):
    """
    Feedback / contact page.
    - Message field is NOT rendered with | safe, so XSS scripts
      are displayed as plain text (Django auto-escaping).
    """
    feedbacks = Feedback.objects.all()[:10]

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            # Attach feedback to logged-in user if available
            if request.user.is_authenticated:
                feedback.user = request.user
            feedback.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('contact')
    else:
        form = FeedbackForm()

    return render(request, 'restaurant/contact.html', {'form': form, 'feedbacks': feedbacks})


# ---------------------------------------------------------------------------
# Authentication views
# ---------------------------------------------------------------------------

def login_view(request):
    """
    Secure login.
    Uses Django's AuthenticationForm which calls authenticate() internally —
    no raw SQL concatenation.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SecureLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = SecureLoginForm(request)

    return render(request, 'restaurant/login.html', {'form': form})


def register_view(request):
    """
    Secure registration.
    Uses UserCreationForm — enforces all AUTH_PASSWORD_VALIDATORS
    configured in settings.py (min 8 chars, no common passwords, etc.)
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome!')
            return redirect('home')
    else:
        form = RegistrationForm()

    return render(request, 'restaurant/register.html', {'form': form})


def logout_view(request):
    """Logout — accepts POST only to prevent CSRF-based forced logout."""
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been logged out.')
    return redirect('home')


# ---------------------------------------------------------------------------
# Authenticated views
# ---------------------------------------------------------------------------

@login_required
def profile_view(request):
    """
    Shows the logged-in user's own profile only.
    No user ID in the URL — prevents IDOR (Insecure Direct Object Reference).
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'restaurant/profile.html', {'form': form, 'profile': profile})


# ---------------------------------------------------------------------------
# Admin view
# ---------------------------------------------------------------------------

# VULN: Exposed Admin Page — no @login_required or @user_passes_test.
# Any unauthenticated visitor can access /admin-panel/ directly.
def admin_panel_view(request):
    """
    INTENTIONALLY VULNERABLE: No authentication check.
    Any user (logged in or not) can view all users and feedback.
    """
    users = User.objects.select_related('profile').all()
    feedbacks = Feedback.objects.select_related('user').all()
    orders = Order.objects.select_related('user').prefetch_related('items__burger').all()
    return render(request, 'restaurant/admin_panel.html', {
        'users': users,
        'feedbacks': feedbacks,
        'orders': orders,
    })


@user_passes_test(_is_staff)
def update_order_status(request, pk):
    """Allow staff to update the status of any order."""
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=pk)
        new_status = request.POST.get('status')
        valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
        if new_status in valid_statuses:
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.pk} marked as "{order.get_status_display()}".')
        else:
            messages.error(request, 'Invalid status selected.')
    return redirect('admin_panel')


# ---------------------------------------------------------------------------
# Cart / Order views
# ---------------------------------------------------------------------------

@login_required
def add_to_cart(request, pk):
    """Add one burger to the session cart (or increment quantity)."""
    burger = get_object_or_404(Burger, pk=pk, is_available=True)
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        key  = str(pk)
        cart[key] = cart.get(key, 0) + 1
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, f'{burger.name} added to your cart!')
    return redirect('cart')


@login_required
def cart_view(request):
    """Display current session cart with totals."""
    cart       = request.session.get('cart', {})
    items      = []
    grand_total = 0
    for burger_id, qty in cart.items():
        try:
            burger   = Burger.objects.get(pk=int(burger_id))
            subtotal = burger.price * qty
            grand_total += subtotal
            items.append({'burger': burger, 'qty': qty, 'subtotal': subtotal})
        except Burger.DoesNotExist:
            pass
    return render(request, 'restaurant/cart.html', {
        'items': items,
        'grand_total': grand_total,
    })


@login_required
def remove_from_cart(request, pk):
    """Remove a burger entirely from the session cart."""
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        cart.pop(str(pk), None)
        request.session['cart'] = cart
        request.session.modified = True
        messages.info(request, 'Item removed from cart.')
    return redirect('cart')


@login_required
def update_cart(request, pk):
    """Set exact quantity for a burger in the session cart."""
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        try:
            qty = int(request.POST.get('qty', 1))
        except (ValueError, TypeError):
            qty = 1
        if qty <= 0:
            cart.pop(str(pk), None)
        else:
            cart[str(pk)] = qty
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('cart')


@login_required
def orders_view(request):
    """Show all past orders for the logged-in user, newest first."""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__burger').order_by('-created_at')
    return render(request, 'restaurant/orders.html', {'orders': orders})


@login_required
def checkout_view(request):
    """Convert session cart into an Order record, then clear the cart."""
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, 'Your cart is empty!')
            return redirect('cart')
        order = Order.objects.create(user=request.user)
        for burger_id, qty in cart.items():
            try:
                burger = Burger.objects.get(pk=int(burger_id), is_available=True)
                OrderItem.objects.create(order=order, burger=burger, quantity=qty)
            except Burger.DoesNotExist:
                pass
        request.session['cart'] = {}
        request.session.modified = True
        messages.success(request, f'Order #{order.pk} placed! We\'ll have it ready soon 🍔')
        return redirect('orders')
    return redirect('cart')
