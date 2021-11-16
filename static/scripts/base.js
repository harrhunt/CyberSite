$(document).ready(function() {

   let bengal = $(".footer-logo")
   let secret = "3838404037393739666513";
   let input = "";
   let timer;

   function checkInput() {
      if (input === secret) {
         bengal.css({"position": "fixed", "top": "50%", "left": "50%", "transform": "translateX(-50%)", "z-index": "100", "width": "auto"});
         bengal.animate({"height": "200%", "top": "-50%"}, 300, function() {
            bengal.css({"position": "", "top": "", "left": "", "transform": "", "height": "", "width": ""})
         });
      }
   }

   $(document).on('keyup', function (e) {
      input += e.which;
      clearTimeout(timer);
      timer = setTimeout(() => input = "", 500);
      checkInput();
   });
});