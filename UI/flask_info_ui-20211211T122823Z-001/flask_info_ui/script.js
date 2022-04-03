//https://www.jitsejan.com/python-and-javascript-in-flask

$.ajax({
  type: "GET",
  url: "~/face",
  data: { param: text}
}).done(function( result ) {
   console.log(result)
});
