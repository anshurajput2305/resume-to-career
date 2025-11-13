async function uploadResume() {
  const input = document.getElementById("resumeInput");
  const file = input.files[0];
  const resultList = document.getElementById("resultList");

  if (!file) return alert("⚠️ Please select a resume file first!");

  const formData = new FormData();
  formData.append("file", file);

  resultList.innerHTML = `<li>⏳ Analyzing your resume, please wait...</li>`;

  try {
    const res = await fetch("/recommend_jobs", { method: "POST", body: formData });
    const data = await res.json();

    resultList.innerHTML = "";

    const extracted_skills = data.extracted_skills || [];
const recommended_jobs =
  data.model_output?.job_roles ||
  data.model_output?.suggested_roles ||
  data.model_output?.recommended_roles ||
  data.model_output?.job_recommendations || 
  data.model_output?.recommended_job_roles ||
  data.model_output?.suggested_job_roles ||
   // <-- add this new key
  [];

    const live_jobs = data.live_jobs || [];

    // Show Extracted Skills
    const skillItem = document.createElement("li");
    skillItem.innerHTML = `<strong>🧠 Extracted Skills:</strong> ${extracted_skills.join(", ") || "No skills detected"}`;
    resultList.appendChild(skillItem);

    // Show Recommended Jobs
    const jobHeader = document.createElement("li");
    jobHeader.innerHTML = `<strong>💼 Recommended Jobs:</strong>`;
    resultList.appendChild(jobHeader);
 if (live_jobs.length > 0) {
      live_jobs.forEach(job => {
        const li = document.createElement("li");
        li.innerHTML = `
          • <a href="${job.link}" target="_blank">${job.title}</a>
            — ${job.company || "Unknown Company"}
            (${job.location || "Remote"})
            ${job.salary ? `<em> - ${job.salary}</em>` : ""}
        `;
        resultList.appendChild(li);
      });
    }
    else if (recommended_jobs.length > 0) {
      recommended_jobs.forEach(job => {
        const li = document.createElement("li");
        li.innerHTML = `• ${job}`;
        resultList.appendChild(li);
      });
    } else {
      const li = document.createElement("li");
      li.textContent = "No job recommendations found.";
      resultList.appendChild(li);
    }

  } catch (err) {
    console.error("Error:", err);
    resultList.innerHTML = `<li>❌ Error analyzing resume. Please try again.</li>`;
  }
}


