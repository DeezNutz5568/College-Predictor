document.getElementById("predictForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const form = new FormData(e.target);
  const params = new URLSearchParams(form).toString();

  const res = await fetch(`/predict?${params}`);
  const data = await res.json();

  document.getElementById("form-container").style.marginTop = "20px";

  const resultsDiv = document.getElementById("results");
  resultsDiv.classList.remove("hidden");
  resultsDiv.innerHTML = "";

  if (data.length === 0) {
    resultsDiv.innerHTML = "<p>No results found. Try adjusting your inputs.</p>";
    return;
  }

  data.forEach(college => {
    const card = document.createElement("div");
    card.classList.add("card");

    const img = document.createElement("img");
    img.src = college.image_url;
    img.onerror = () => {
      img.src = "/images/default.jpg";
    };

    const title = document.createElement("h2");
    title.textContent = college.institute;

    const list = document.createElement("ul");
    college.programs.forEach(prog => {
      const item = document.createElement("li");
      item.textContent = `${prog.program} (CR: ${prog.closing_rank})`;
      list.appendChild(item);
    });

    card.appendChild(img);
    card.appendChild(title);
    card.appendChild(list);

    resultsDiv.appendChild(card);
  });
});
