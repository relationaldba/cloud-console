// htmx.config.responseHandling = [
//   { code: "204", swap: false }, // 204 - No Content by default does nothing, but is not an error
//   { code: "[23]..", swap: true }, // 200 & 300 responses are non-errors and are swapped
//   { code: "[45]..", swap: false, error: true }, // 400 & 500 responses are not swapped and are errors
//   { code: "...", swap: true }, // catch all for any other response code
// ];

// Handle the response errors, show a modal with details of the operation
htmx.on("htmx:response-error", (error) => {

  if (error.detail.xhr.status < 400) {
    return;
  }
  // if (error.detail.xhr.status === 401) {
  //   toggle401ErrorModal(error);
  // }
  // if (error.detail.xhr.status === 404) {
  //   toggle404ErrorModal(error);
  // } 
  else {
    toggleGenericErrorModal(error);
  }
});




/***** Inline Editable *****/
// $("input.inline-editable").on("blur", function (event) {
//   $(this).attr("readonly");
//   // $(this).removeClass("readwrite");
//   // $(this).addClass("readonly");
// });

// $("input.inline-editable").on("dblclick", function (event) {
//   $(this).removeAttr("readonly");
//   // $(this).removeClass("readonly");
//   // $(this).addClass("readwrite");
//   //$(this).focus();
// });