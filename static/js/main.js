function addToCart(name, price, image) {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    cart.push({ name, price, image });

    localStorage.setItem("cart", JSON.stringify(cart));
    loadCart(); 
    showToast();
}

//---Start shopping cart -----
function loadCart() {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    let cartList = document.getElementById("cart-items");
    cartList.innerHTML = "";

    if (cart.length === 0) {
        cartList.innerHTML = "<li class='list-group-item text-center'>🚀 عربة التسوق فارغة!</li>";
        return;
    }

    let totalPrice = 0;

    cart.forEach((item, index) => {
        let li = document.createElement("li");
        li.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-center");
        li.innerHTML = `
            <img src="${item.image}" width="50" class="rounded">
            <span><strong>EGP ${item.price}</strong> - ${item.name} </span>
            <button class="btn btn-sm btn-secondary" onclick="removeFromCart(${index})">❌</button>
        `;
        cartList.appendChild(li);


        totalPrice += parseFloat(item.price);
    });


    let totalElement = document.getElementById("total-price");
    if (totalElement) {
        totalElement.innerHTML = `<strong>EGP ${totalPrice.toFixed(2)}</strong> : الاجمالي `;
    }

}
//---End shopping cart -----

//--- -----
function removeFromCart(index) {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    cart.splice(index, 1);
    localStorage.setItem("cart", JSON.stringify(cart));
    loadCart();
}

function clearCart() {
    localStorage.removeItem("cart");
    loadCart();
}



//--- orders----

document.getElementById("order-form").addEventListener("submit", function (event) {
    event.preventDefault();
    let name = document.getElementById("customer-name").value;
    let phone = document.getElementById("customer-phone").value;
    let address = document.getElementById("customer-address").value;

    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    
    let totalPrice = cart.reduce((total, item) => total + parseFloat(item.price), 0);

    let productDetails = cart.map(item => `📦 ${item.name} - 💰 ${item.price} EGP`).join("\n");


    let message = `طلب جديد:\n${productDetails}\n\n👤 الاسم: ${name}\n📞 الهاتف: ${phone}\n📍 العنوان: ${address}\n\n💵 الإجمالي: ${totalPrice.toFixed(2)} EGP`;


    let whatsappURL = `whatsapp://send?phone={Enter Phone Number Here}&text=${encodeURIComponent(message)}`;


    localStorage.removeItem("cart");


    window.location.href = whatsappURL;


    function goToCheckout() {
        window.location.href = "{{ url_for('index') }}";
    }
});

// ---- one order---
document.getElementById("order-form").addEventListener("submit", function (event) {
    event.preventDefault();

    const productName = document.getElementById("data-name").getAttribute("data-name");
    const productDescription = document.getElementById("data-description").getAttribute("data-description");
    const productPrice = document.getElementById("data-price").getAttribute("data-price");


    const customerName = document.getElementById("customer-name").value;
    const customerPhone = document.getElementById("customer-phone").value;
    const customerAddress = document.getElementById("customer-address").value;


    if (!customerName || !customerPhone || !customerAddress) {
        alert("يرجى ملء جميع الحقول المطلوبة!");
        return;
    }


    const message = `طلب جديد:\n\n`
        + `📦 المنتج: ${productName}\n`
        + `📝 الوصف: ${productDescription}\n`
        + `💰 السعر: ${productPrice} EGP\n\n`
        + `👤 اسم العميل: ${customerName}\n`
        + `📞 رقم الهاتف: ${customerPhone}\n`
        + `📍 العنوان: ${customerAddress}`;


    const phoneNumber = "{Enter Phone Number Here}";
    const whatsappURL = `https://wa.me/${phoneNumber}?text=${encodeURIComponent(message)}`;


    window.location.href = whatsappURL;
});



// Function to show toast notification
function showToast() {
    var toast = new bootstrap.Toast(document.getElementById('success-toast'));
    toast.show();
}

//-----------

function goToCheckout() {

    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    
    if (cart.length === 0) {
        alert("سلة التسوق فارغة. لا يمكن استكمال الشراء.");
    } else {
        window.location.href = "{{ url_for('checkout') }}"; 
    }
}


function clearCart() {
    localStorage.removeItem("cart"); 
    updateCartDisplay(); 
}


function updateCartDisplay() {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    let cartList = document.getElementById("cart-items");
    

    cartList.innerHTML = "";

    cart.forEach(item => {
        let li = document.createElement("li");
        li.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-center");
        li.innerHTML = `
            <img src="${item.image}" width="50" class="rounded">
            <span>${item.name} - <strong>${item.price} EGP</strong></span>
            <button class="btn btn-sm btn-secondary" onclick="removeFromCart(${item.id})">❌</button>
        `;
        cartList.appendChild(li);
    });


    let totalPrice = cart.reduce((total, item) => total + parseFloat(item.price), 0);
    document.getElementById("total-price").textContent = `إجمالي: EGP ${totalPrice.toFixed(2)}`;
}


document.addEventListener("DOMContentLoaded", updateCartDisplay);


