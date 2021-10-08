let prod = new Vue({
    el: '#prod',
    data: {
        categorys: [],
        products: [],
        newPrice: [],
        csrf: getCookie('csrftoken'),
    },
    created: async function () {
        const t = this;
        await fetch('/api/category/', {method: 'GET'})
            .then(async response => {
                t.categorys = await response.json();
            });
        await fetch('/api/products/', {method: 'GET'})
            .then(async response => {
                let data = await response.json();
                data.forEach(function (item) {
                    t.newPrice[item.id] = item.price;
                });
                t.categorys.forEach(function (item) {
                    t.products.push(data.filter(j => j.category.name === item.name))
                })
            })
    },
    methods: {
        price(i, j) {
            this.newPrice.splice(i, 1, j)
        },
        async post(slug, sizePizza, i, promotions = false) {
            value = sizePizza.target.querySelector('input[name="size"]:checked').value
            const requestOptions = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrf
                },
                body: JSON.stringify({
                    price: this.newPrice[i]
                })
            }
            const result = await fetch(`/add/${slug}/?size=${value}`, requestOptions).then(nav.reload)
        }

    }
})

let nav = new Vue({
    el: '#category',
    data: {
        category: [],
        cartProducts: [],
        count: 0
    },
    created: async function () {
        const t = this;
        await fetch('/api/category/', {method: 'GET'})
            .then(async response => {
                t.category = await response.json();
            });
        await fetch('/api/cart/', {method: 'GET'})
            .then(async response => {
                let data = await response.json();
                t.cartProducts = data[0];
                try {
                    t.count = t.cartProducts.qty
                } catch (e) {
                }
                ;
            })
    },
    methods: {
        async reload() {
            const t = this;
            await fetch('/api/cart/', {method: 'GET'})
                .then(async response => {
                    let data = await response.json();
                    t.cartProducts = data[0];
                    t.count = t.cartProducts.qty;
                })
        }
    }
})

let promotions = new Vue({
    el: '#promotions',
    data: {
        promotions: [],
        modalObject: [],
        category: ''
    },
    created: async function () {
        const t = this;
        await fetch('/api/promotions/', {method: 'GET'})
            .then(async response => {
                t.promotions = await response.json();
                if (t.promotions.length === 0) {
                    t.promotions = false;
                }
            })
    },
    methods: {
        async modal(id) {
            const t = this;
            await fetch(`/api/products/${id}/`, {method: 'GET'})
                .then(async response => {
                    t.modalObject = await response.json();
                    prod.newPrice[t.modalObject.id] = t.modalObject.price;
                    t.category = t.modalObject.category.name;
                })
        },
    }
})
let app2 = new Vue({
    el: '#street',
    data: {
        search: '',
        streets: [],
        error: 'Простите, мы доставляем в радиусе 3 км.',
        dist: 0,
        seen: true,
        phone: '',
    },
    created: async function () {
        const t = this;
        await fetch('/api/user/', {method: 'GET'})
            .then(async response => {
                let data = await response.json();
                t.phone = data[0]?.phone;
            })
    },
    methods: {
        async searchStreet() {
            await fetch(`https:nominatim.openstreetmap.org/search?q=Томск+${this.search}&format=json&limit=3`, {method: 'GET'})
                .then(async response => {
                        this.streets = await response.json();
                        if (this.streets.length === 0) {
                            this.streets = [{display_name: 'Ничего не найдено.'}]
                        } else {
                            this.streets.forEach(function (item) {
                                item.display_name = item.display_name.slice(0, getListIdx(item.display_name, ',')[1])
                            })
                        }
                    }
                )
        },
        choiceStreet(str, lat, lon) {
            this.dist = getDistanceFromLatLonInKm(56.4720791, 84.96071130123357, lat, lon);
            if (this.dist < 3) {
                console.log(this.dist)
                this.search = str;
                this.streets = [];
                buy.choice = false;
                err.seen = false;
            } else {
                err.seen = true
                console.log(this.dist)
            }
        },
        changeS() {
            buy.choice = true;
        },
    },

})

let buy = new Vue({
    el: '#payment',
    data: {
        choice: true,
        select: ''
    },
    methods: {
        async socket() {
            let socketWS = new WebSocket('ws://localhost:8000/order/');
            socketWS.onopen = () => socketWS.send(JSON.stringify({
                'message': '3ddqwd'
            }))
        }
    },
    watch: {
        select(q) {
            app2.seen = q !== 'self';
            if (q === 'self') {
                this.choice = false;
                err.seen = false;
            }
        }
    }
})

let err = new Vue({
    el: '#err',
    data: {
        error: 'Простите, мы доставляем в радиусе 3 км.',
        seen: false
    }
})

let basket = new Vue({
    el: '#basket',
    data: {
        cart: [],
        csrf: getCookie('csrftoken'),
        code: '',
        status: ''
    },
    created: async function () {
        const t = this;
        await fetch('/api/cart/', {method: 'GET'})
            .then(async response => {
                let data = await response.json()
                t.cart = data[0];
            })
    },
    methods: {
        async coupon(code) {
            const requestOptions = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrf
                },
                body: JSON.stringify({
                    'code': code,
                })
            }
            const t = this;
            const result = await fetch('/basket/', requestOptions)
                .then(async response => {
                    let data = await response.json();
                    t.status = data.data;
                    await fetch('/api/cart/', {method: 'GET'})
                        .then(async response => {
                            let data = await response.json()
                            t.cart = data[0];
                        })
                })
        },
        buttom() {
            if (this.status === 'Такого промокода нет.' || this.status === 'Промокод активирован') {
                this.status = 'Промокод активирован';
                return 'btn-success'
            } else if (this.status === 'Чтобы использовать промокод надо авторизоваться.') {
                return 'btn-danger'
            } else if (this.status === 'Этот промокод уже был использован.') {
                return 'btn-warning'
            }
        },
        async delCoupon() {
            const requestOptions = {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrf
                }
            }
            const t = this;
            const result = await fetch('/basket/', requestOptions)
                .then(async response => {

                    await fetch('/api/cart/', {method: 'GET'})
                        .then(async response => {
                            let data = await response.json()
                            t.cart = data[0];
                            t.status = '';
                        })
                })
        },
        async deleteProduct(slug, size) {
            const requestOptions = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrf
                },
                body: JSON.stringify({
                    size: size,
                })

            }
            const t = this;
            const result = await fetch('/remove-from-cart/' + slug + '/', requestOptions)
                .then(async () =>
                    await fetch('/api/cart/', {method: 'GET'})
                        .then(async response => {
                            let data = await response.json();
                            t.cart = data[0];
                            nav.reload()
                        })
                )
        },
        async changeQTY(slug, size, qtyN, num) {
            const requestOptions = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrf
                },
                body: JSON.stringify({
                    size: size,
                    qty: Number(qtyN + num)
                })

            }
            const t = this;
            const result = await fetch('/change-qty/' + slug + '/', requestOptions)
                .then(async () =>
                    await fetch('/api/cart/', {method: 'GET'})
                        .then(async response => {
                            let data = await response.json();
                            t.cart = data[0];
                            nav.count += num;
                        })
                );
        }
    }

})


let custom = new Vue({
    el: '#custom',
    data: {
        final_cost: [],
        meat: meats,
        vegetable: vegetables,
        cheese: cheeses,
        ingredients: [],
        dough: 1,
        size: 1,
        filter: 'meat',
        csrf: getCookie('csrftoken'),
    },
    methods: {
        addProd(prod, price, i) {
            if (prod.trues) {
                prod.style = 'prodDel';
                this.final_cost.push({prod: prod.prod, qty: 1, cost: price});
            } else {
                const idx = this.final_cost.indexOf(this.final_cost.find(src => src.prod === prod.prod));
                if (idx !== -1) {
                    prod.style = 'prodPlus';
                    this.final_cost.splice(idx, 1);
                }
            }

            prod.trues = !prod.trues;
        },
        ingredientsList() {
            if (this.filter === 'meat') {
                return this.meat;
            } else if (this.filter === 'cheese') {
                return this.cheese;
            } else if (this.filter === 'vegetable') {
                return this.vegetable;
            }
        },
        sizeImg() {
            if (this.size === 1) {
                return {'width': '70%'}
            } else if (this.size === 1.2) {
                return {'width': '85%'}
            } else if (this.size === 1.4) {
                return {'width': '100%'}
            }
        },
        removeProd(i) {
            const idx = this.final_cost.indexOf(i);
            this.final_cost.splice(idx, 1);
            if (this.meat.indexOf(this.meat.find(src => src.prod === i.prod)) >= 0) {
                const idx = this.meat.indexOf(this.meat.find(src => src.prod === i.prod));
                this.meat[idx].style = 'prodPlus';
                this.meat[idx].trues = !this.meat[idx].trues;
            }
            if (this.cheese.indexOf(this.cheese.find(src => src.prod === i.prod)) >= 0) {
                const idx = this.cheese.indexOf(this.cheese.find(src => src.prod === i.prod))
                this.cheese[idx].style = 'prodPlus'
                this.cheese[idx].trues = !this.cheese[idx].trues;
            }
            if (this.vegetable.indexOf(this.vegetable.find(src => src.prod === i.prod)) >= 0) {
                const idx = this.vegetable.indexOf(this.vegetable.find(src => src.prod === i.prod));
                this.vegetable[idx].style = 'prodPlus';
                this.vegetable[idx].trues = !this.vegetable[idx].trues;
            }
        },
        changeQty(i, num, classes) {
            const idx = this.final_cost.indexOf(i);
            this.final_cost[idx].qty = num;

        },
        doughChoice(event) {
            if (event === 0)
                this.dough = 1
            else if (event === 1)
                this.dough = 1.1
        },
        sizeChoice(event) {
            if (event === 0)
                this.size = 1
            if (event === 1)
                this.size = 1.1
            else if (event === 2)
                this.size = 1.2
        },
        price() {
            let price = 225;
            this.final_cost.forEach(function (item) {
                price += item.cost * item.qty
            });
            return Math.ceil(price * this.dough * this.size);
        },
        async post() {
            let doughStr;
            let sizeStr;
            let descriptionStr;
            if (this.size === 1)
                sizeStr = 25
            else if (this.size === 1.1)
                sizeStr = 30
            else if (this.size === 1.2)
                sizeStr = 35
            if (this.dough === 1)
                doughStr = 'Тонкое тесто, '
            else if (this.dough === 1.1)
                doughStr = 'Традиционное тесто, '
            descriptionStr = doughStr;
            descriptionStr += this.final_cost.map(({prod, qty}) => `${prod} ${qty}`).join(', ');
            const requestOptions = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrf
                },
                body: JSON.stringify({
                    description: descriptionStr,
                    price: this.price(),
                    custom: true,
                    size: sizeStr,
                    slug: randStr(11)
                })
            }
            const result = await fetch(`/custom/`, requestOptions).then(nav.reload);
            this.final_cost = []
        },
    }
})
let staff = new Vue({
    el: '#staff',
    data: {
        error: '',
        orders: [],
        status: ['new', 'in_progress', 'is_ready', 'completed'],
        csrf: getCookie('csrftoken'),
        page: 0,
        pages: 0
    },
    methods: {
        bg(status, stChange = false) {
            if (!stChange && status) {
                if (status === 'new')
                    return 'alert-dark'
                if (status === 'in_progress')
                    return 'alert-primary'
                if (status === 'is_ready')
                    return 'alert-warning'
                if (status === 'completed')
                    return 'alert-success'
                if (status === 'canceled')
                    return 'alert-danger'
            } else {
                if (status === 'new')
                    return 'btn-dark'
                if (status === 'in_progress')
                    return 'btn-primary'
                if (status === 'is_ready')
                    return 'btn-warning'
                if (status === 'completed')
                    return 'btn-success'
            }
        },
        async changeStatus(st, id, checkSt) {
            if (st !== checkSt) {
                const requestOptions = {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.csrf
                    },
                    body: JSON.stringify({
                        id: id,
                        status: st,
                    })
                }
                await fetch(`/staff/`, requestOptions);
                const chatSocket = new WebSocket('ws://localhost:8000/order/');
            }
        },
        ordersSort() {
            let newOrders = [];
            this.orders.filter(item => item.status === 'new').forEach(function (item) {
                newOrders.push(item)
            });
            this.orders.filter(item => item.status === 'in_progress').forEach(function (item) {
                newOrders.push(item)
            });
            this.orders.filter(item => item.status === 'is_ready').forEach(function (item) {
                newOrders.push(item)
            });
            this.orders.filter(item => item.status === 'completed').forEach(function (item) {
                newOrders.push(item)
            });
            let size = 5;
            this.pages = Math.ceil(newOrders.length / size);
            for (let i = 0; i < this.pages; i++) {
                newOrders[i] = newOrders.slice((i * size), (i * size) + size);
            }
            return newOrders[this.page];
        }
    }
})


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function getDistanceFromLatLonInKm(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const dLat = deg2rad(lat2 - lat1);
    const dLon = deg2rad(lon2 - lon1);
    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2)
    ;
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

function deg2rad(deg) {
    return deg * (Math.PI / 180)
}


function getListIdx(str, substr) {
    let listIdx = []
    let lastIndex = -1
    while ((lastIndex = str.indexOf(substr, lastIndex + 1)) !== -1) {
        listIdx.push(lastIndex)
    }
    return listIdx
}

function randStr(size = 5) {
    let result = [];
    let characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let charactersLength = characters.length;
    for (let i = 0; i < size; i++) {
        result.push(characters.charAt(Math.floor(Math.random() *
            charactersLength)));
    }
    return result.join('');
}

$(document).ready(function () {

    $('#tel').inputmask("9-999-999-99-99");
    $('#id_phone').inputmask("9-999-999-99-99");
});

$(document).on('submit', 'form#main', function () {
    const chatSocket = new WebSocket(
        'ws://localhost:8000/order/');
});
$('#delOrder').click(async function () {
    const requestOptions = {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    }
    const t = this;
    const result = await fetch('/basket/order/', requestOptions)
        .then(async response => {
            const chatSocket = new WebSocket('ws://localhost:8000/order/');
            chatSocket.onmessage = function (e) {
            };
            window.location = '/basket/order/';
        });
})