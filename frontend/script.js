async function uploadResume() {
  const input = document.getElementById("resumeInput");
  const file = input.files[0];

  if (!file) {
    alert("⚠️ Please select a resume file first!");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  const jobList = document.getElementById("jobList");
  jobList.innerHTML = `<li>⏳ Analyzing your resume...</li>`;

  try {
    const response = await fetch("http://127.0.0.1:8000/upload_resume", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      throw new Error("Upload failed");
    }

    const data = await response.json();
    console.log("Response from backend:", data);

    const { extracted_skills = [], recommended_jobs = [], upskill_recommendations = [] } = data;

    jobList.innerHTML = "";

    if (recommended_jobs.length === 0) {
      jobList.innerHTML = `<li>No job matches found.</li>`;
    } else {
      recommended_jobs.forEach(job => {
        const li = document.createElement("li");
        li.className = "bg-blue-50 p-3 rounded-lg hover:bg-blue-100 transition-all";
        // For HuggingFace response (title + score)
        if (typeof job === "object" && job.title) {
          li.innerHTML = `<strong>${job.title}</strong> – Match: <span class="text-blue-600">${job.score}%</span>`;
        } else {
          li.innerHTML = `<strong>${job}</strong>`;
        }
        jobList.appendChild(li);
      });
    }

    // Optional: show extracted skills
    let skillsContainer = document.getElementById("skills");
    if (!skillsContainer) {
      skillsContainer = document.createElement("div");
      skillsContainer.id = "skills";
      skillsContainer.className = "mt-4 text-gray-700";
      jobList.insertAdjacentElement("afterend", skillsContainer);
    }
    skillsContainer.innerHTML = `<strong>🧠 Extracted Skills:</strong> ${extracted_skills.join(", ") || "None detected"}`;

    // Optional: show upskill suggestions
    let upskillContainer = document.getElementById("upskills");
    if (!upskillContainer) {
      upskillContainer = document.createElement("div");
      upskillContainer.id = "upskills";
      upskillContainer.className = "mt-2 text-gray-700";
      skillsContainer.insertAdjacentElement("afterend", upskillContainer);
    }
    upskillContainer.innerHTML = `<strong>📈 Suggested Upskills:</strong> ${upskill_recommendations.join(", ") || "None"}`;

  } catch (error) {
    console.error("Error:", error);
    jobList.innerHTML = `<li>❌ Error analyzing resume. Please try again.</li>`;
  }
}
