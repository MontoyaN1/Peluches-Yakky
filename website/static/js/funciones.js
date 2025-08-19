$('.plus-cart').click(function () {
    console.log("Buton click")

    var id = $(this).attr('pid').toString()
    var cantidad = this.parentNode.children[2]

    $.ajax({
        type: 'GET',
        url: '/pluscart',
        data: {
            cart_id: id
        },
        success: function (data) {
            console.log(data)
            cantidad.innerText = data.cantidad
            document.getElementById(`quantity${id}`).innerText = data.cantidad
            document.getElementById('subtotal_st').innerText = data.subtotal
            document.getElementById('total_t').innerText = data.total

        }
    })
})

$('.minus-cart').click(function () {
    console.log("Buton click")

    var id = $(this).attr('pid').toString()
    var cantidad = this.parentNode.children[2]

    if (cantidad <= 1) {
        return false

    } $.ajax({
        type: 'GET',
        url: '/minuscart',
        data: {
            cart_id: id
        },
        success: function (data) {
            console.log(data)

            if (data.cantidad >= 1) {
                cantidad.innerText = data.cantidad
                document.getElementById(`quantity${id}`).innerText = data.cantidad
                document.getElementById('subtotal_st').innerText = data.subtotal
                document.getElementById('total_t').innerText = data.total

            }


        }
    })
})

$('.remove-cart').click(function () {

    var id = $(this).attr('pid').toString()

    var to_remove = this.parentNode.parentNode.parentNode.parentNode

    $.ajax({
        type: 'GET',
        url: '/removecart',
        data: {
            cart_id: id
        },

        success: function (data) {
            document.getElementById('subtotal_st').innerText = data.amount
            document.getElementById('total_t').innerText = data.total
            to_remove.remove()
        }
    })


})


