(function () {
  "use strict";

  var isLocal =
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1";

  window.BERTOLLI_API_BASE_URL =
    window.BERTOLLI_API_BASE_URL ||
    (isLocal ? "http://localhost:8005" : "https://prueba-tecnica-xe6q.onrender.com");
})();
