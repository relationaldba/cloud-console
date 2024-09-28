
// Toggle modal when HTTP 401 (not authenticated) error occurs
// const toggle401ErrorModal = (event) => {
//   event.preventDefault();
//   console.log("modal is being created by js");

//   const modal = document.createElement("dialog");
//   modal.id = "login-modal";
//   htmx.ajax("GET", "/login", { target: "#login-modal", swap: "outerHTML" });
//   document.body.appendChild(modal);
//   modal.showModal();
// };

// const toggle404ErrorModal = (event) => {
//   event.preventDefault();

//   const article = document.createElement("article");
//   const footer = document.createElement("footer");
//   const dismiss = document.createElement("button");
//   const modal = document.createElement("dialog");
//   article.innerHTML = `<h3>Oops, the resource cound not be found!</h3><p>We were not able to find the requested resource. Please verify if the resource exists and you have access to it.<br>[${event.detail.error}]</p>`;
//   dismiss.id = "dismiss-modal-btn";
//   dismiss.innerHTML = "Dismiss";
//   footer.appendChild(dismiss);
//   article.appendChild(footer);
//   modal.appendChild(article);
//   modal.id = "modal";
//   document.body.appendChild(modal);
//   modal.showModal();
//   htmx.on("#dismiss-modal-btn", "click", () => {
//     modal.remove();
//   });
// };


// Toggle modal when any error occurs
const toggleGenericErrorModal = (event) => {
  event.preventDefault();

  // create a dialog modal
  const modal = document.createElement("dialog");
  modal.classList.add("modal");

  // create an underlay div
  const underlay = document.createElement("div");
  underlay.id = "modal-underlay";
  underlay.classList.add("modal-underlay");

  // create an article with the error message
  const article = document.createElement("article");
  article.classList.add("modal-content");
  article.innerHTML = `<h3>Oops, an error occurred!</h3><p>We ran into an error while processing your request. Please try again later or contact support if the problem persists.<br>[${event.detail.error}]</p>`;
  
  const footer = document.createElement("footer");
  const close_btn = document.createElement("button");
  close_btn.id = "dismiss-modal-btn";
  close_btn.innerHTML = "Close";
  close_btn.classList.add("Secondary");

  footer.appendChild(close_btn);
  article.appendChild(footer);

  // add the elements to the modal
  modal.appendChild(underlay);
  modal.appendChild(article);
  document.body.appendChild(modal);
  modal.showModal();

  htmx.on("#dismiss-modal-btn", "click", () => {
    modal.remove();
  });

  htmx.on("#modal-underlay", "click", () => {
    modal.remove();
  });
};
