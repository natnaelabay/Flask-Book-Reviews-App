const searchForm = document.querySelector("#search-form");
const errors = document.querySelector(".errors");
searchForm.addEventListener("submit", (e) => {
  e.preventDefault();
  let searchBox = document.querySelector("#payload");
  const search_svg = document.querySelector(".search-svg-wrapper")

  let searchType = document.querySelector("#search-type");
  errors.innerHTML ="" 
  if (searchBox.value == "" || searchType.value == "") {
    console.log("select a type");
    errors.innerHTML += `
    <div class="alert mx-2 h-25  alert-success" role="alert">
       Both search payload and Type are needed!
    </div>
    `;
  } else {

    axios.get(`/search?payload=${searchBox.value}&search_category=${searchType.value}`)
    .then(res => {
        const r = res.data;
        const search_aggregator = document.querySelector(".search-content")
        if(r.success == true) {
          search_svg.classList.add("d-none")
          if (r.data.length == 0) {
            search_aggregator.innerHTML += `
          <h1 class = 'search-svg-wrapper'>No Books Found</h1>`
          }
          else {
            search_aggregator.style.height = "auto" 
            books = r.data;
            search_aggregator.innerHTML = ""
            
            for (let i = 0; i < 5; i++) {
              // console.log(books[i]);
              // break;
              search_aggregator.innerHTML += `
                <a href="/book-review/${books[i].isbn}" >
                  <div class="search-box mt-3" style="position: relative;">
                      <div class="left">
                          <img src="static/images/a.png" alt="">
                      </div>
                      <div class="middle">
                          <p>${books[i].title}</p>
                      </div>
                      <div class="right">
                          <p>By. <span>${books[i].author}</span></p>
                      </div>
                  </div>
                  <input name="book_id" type="text" class="d-none" value="${books[i].isbn}" />
                </a>
                `
            }
            for (const book  of r.data) {
              console.log("IN HERE");
            }
          }
        }
        console.log(res.data)
    })  .catch(e => {
        console.log(e)
    })
  }
});


document.querySelector("#logout-submit")
.addEventListener("click" , e=> {
    document.querySelector("#logout-form").submit()
})