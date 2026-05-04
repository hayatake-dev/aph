
document.addEventListener("DOMContentLoaded", function () {
  const checkinInput = document.getElementById("checkin-display");
  const checkoutInput = document.getElementById("checkout-display");
  const checkinHidden = document.getElementById("checkin");
  const checkoutHidden = document.getElementById("checkout");
  const calendarPopup = document.getElementById("calendar-popup");
  const calendarMonth1 = document.getElementById("calendar-month1");
  const calendarMonth2 = document.getElementById("calendar-month2");
  const calendarClose = document.getElementById("calendar-close");

  let selecting = null; // "checkin" or "checkout"

  function openCalendar(type) {
    selecting = type;
    calendarPopup.style.display = "block";
    renderCalendar();
  }

  checkinInput.addEventListener("click", () => openCalendar("checkin"));
  checkoutInput.addEventListener("click", () => openCalendar("checkout"));
  calendarClose.addEventListener("click", () => calendarPopup.style.display = "none");

  function renderCalendar() {
    const today = new Date();
    const month1 = new Date(today.getFullYear(), today.getMonth(), 1);
    const month2 = new Date(today.getFullYear(), today.getMonth()+1, 1);

    calendarMonth1.innerHTML = buildMonth(month1);
    calendarMonth2.innerHTML = buildMonth(month2);

    document.querySelectorAll(".calendar-month td[data-date]").forEach(td => {
      td.addEventListener("click", () => {
        const selectedDate = td.dataset.date;
        if (selecting === "checkin") {
          checkinInput.value = selectedDate;
          checkinHidden.value = selectedDate;
        } else if (selecting === "checkout") {
          checkoutInput.value = selectedDate;
          checkoutHidden.value = selectedDate;
        }
        calendarPopup.style.display = "none";
      });
    });
  }

  function buildMonth(date) {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1).getDay();
    const lastDate = new Date(year, month + 1, 0).getDate();

    let html = `<table>
      <thead>
        <tr><th colspan="7">${year}年${month+1}月</th></tr>
        <tr><th>日</th><th>月</th><th>火</th><th>水</th><th>木</th><th>金</th><th>土</th></tr>
      </thead>
      <tbody><tr>`;

    for (let i=0; i<firstDay; i++) html += "<td></td>";
    for (let d=1; d<=lastDate; d++) {
      const fullDate = `${year}-${("0"+(month+1)).slice(-2)}-${("0"+d).slice(-2)}`;
      html += `<td data-date="${fullDate}">${d}</td>`;
      if ((d + firstDay) % 7 === 0) html += "</tr><tr>";
    }
    html += "</tr></tbody></table>";
    return html;
  }
});
