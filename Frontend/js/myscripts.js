function showDiv(divId, element) {
    if (element === "freqPoly") {
        document.getElementById(divId).style.display = element.value === 1 ? 'block' : 'none';
    } else {
        document.getElementById(divId).style.display = "none";
    }
}

let i = 0;

function move() {
  if (i === 0) {
    i = 1;
    var elem = document.getElementById("establishResultsBar");
    var width = 1;
    var id = setInterval(frame, 10);
    function frame() {
      if (width >= 100) {
        clearInterval(id);
        i = 0;
      } else {
        width++;
        elem.style.width = width + "%";
      }
    }
  }
}