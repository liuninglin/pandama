function getCSRFToken() {
  let cookies = document.cookie.split(";");
  for (let i = 0; i < cookies.length; i++) {
    let c = cookies[i].trim();
    if (c.startsWith("csrftoken=")) {
      return c.substring("csrftoken=".length, c.length);
    }
  }
  return "unknown";
}

function addWishListDirectly(thisObj, product_number) {
  $(thisObj).children("i").removeClass("far");
  $(thisObj).children("i").addClass("fas");
  
  params={"product_number": product_number};
  commonAjax_alert("store/ajax-add-to-wish-list", "GET", params, "json", "Added to wishlist successfully!");
}

function addCartDirectly(sku) {
  params={sku_number: sku, "quantity": 1};
  commonAjax_alert("store/cart/ajax-add", "POST", params, "json", "Added to cart successfully!");
}

function alertShow(type, message) {
  var message_class = "notification-info"
  if ("error" == type) {
    message_class = "notification-error";
  } else if ("info" == type) {
    message_class = "notification-info";
  } else if ("warn" == type) {
    message_class = "notification-warn";
  }


  $("body").append("<div class='message-show " + message_class + " animated fadeIn'>" + message + "</div>");
  $(".message-show").delay(2000).fadeOut();
}

function commonAjax(url, method, params, returnDataType, successFunction, errorFunction) {
  url = location.protocol + "//" + location.host + "/" + url;
  if (method == "POST" && !params.hasOwnProperty("csrfmiddlewaretoken")) {
    params["csrfmiddlewaretoken"] = getCSRFToken(); 
  }
  
  $.ajax({
      type: method,
      url: url,
      data: params,
      dataType: returnDataType,
      success: successFunction,
      error: errorFunction,
      statusCode: {
        401: function() {
           window.location.href = location.protocol + "//" + location.host + "/store/login";
        }
      }
  }); 
}


function commonAjax_alert(url, method, params, returnDataType, successMessage) {
  commonAjax(url, method, params, returnDataType, function(res){
    if (res.message == "Success") {
        alertShow("info", successMessage);
    } else {
        alertShow("error", "Occurred error!");
    }
  }, function(res){
    alertShow("error", "Occurred error!");
  }); 
}

function goBack() {
  if (document.referrer.indexOf(location.protocol + "//" + location.host) < 0) {
     window.location.href = location.protocol + "//" + location.host + "/store/home"; 
  }

  url_array = ['store/home', 'store/profile', 'store/wish-list', 'store/catalog', 'store/product-list', 'store/product-detail', 'store/cart', 'store/order']

  for (var index in url_array) {
    if (document.referrer.indexOf(url_array[index]) >= 0) {
      window.history.go(-1);
      return;
    } 
  }
  window.location.href = location.protocol + "//" + location.host + "/store/home";
}

var page = 2;
var endFlag = false;
function scroll_load(url, size, div_scroll_locator, scroll_height, done_function) {
    $("#loading_div").show(500);

    if (url.indexOf("?") >= 0) {
      url += ("&page=" + page)
    } else {
      url += ("?page=" + page)
    }

    if (null != size) {
      url += ("&size=" + size)
    }
    
    setTimeout(function() {  
      commonAjax(url, "GET", null, "html", function(html){
        $(div_scroll_locator).append(html);
        $("#loading_div").hide(500);
        page++;
        window.scroll({
          top: scroll_height,
          behavior: 'smooth'
        });
        if (null != done_function){
          done_function();
        }
      }, null);

    }, 1000);
  }

function page_scroll_detector(url, page_size, total_size, div_scroll_locator, done_function) {
  // console.log(($(window).scrollTop() + 100 ) + ":" + ($(document).height() - $(window).height()));
  if (Math.ceil(parseInt(total_size) / parseInt(page_size)) < page){
    if (!endFlag) {
      var alterHTML = '<div style="margin-bottom: 50px;margin-top: 10px;text-align: center;width: 100%;"><p style="font-size: 20px;font-weight: bold;">This is the End!</p></div>';
      $(div_scroll_locator).append(alterHTML); 
      endFlag = true;
    }
    return;
  }

  if ($("#loading_div").css("display") == "none") {
    scroll_height = $(window).scrollTop(); 
  } 
  
  if(($(window).scrollTop() + 100) >= $(document).height() - $(window).height()) {        
    if ($("#loading_div").css("display") == "none") {
      scroll_load(url, page_size, div_scroll_locator, scroll_height - 5, done_function)
    }
  }
}

