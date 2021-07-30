function toggleSidebar(ref){
  document.getElementById("side-bar").classList.toggle('active');
}

toggleSidebar();


$(document).ready(function(){
    //jquery for toggle sub menus
    $('.sub-btn').click(function(){
      $(this).next('.sub-menu').slideToggle();
    });
});




