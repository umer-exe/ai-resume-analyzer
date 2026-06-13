export const REPORT_TABS = ["Overview", "Analysis", "Action Plan"];

export const LOADING_ITEMS = [
  "Reading profile text",
  "Checking profile structure",
  "Extracting skills",
  "Predicting resume category",
  "Preparing action plan",
];

export const SAMPLE_PROFILES = [
  {
    label: "Python Developer",
    value:
      "Computer science graduate and Python developer with experience using " +
      "Flask, Django, SQL, REST APIs, Git, GitHub, Docker, Pandas, and Linux. " +
      "Built a Flask inventory platform that managed more than 2,000 records " +
      "and reduced manual reporting time by 35%. Completed a six-month software " +
      "development internship and documented tested backend services.",
  },
  {
    label: "Front End Developer",
    value:
      "UI Developer with HTML5, CSS3, JavaScript, jQuery, AJAX, AngularJS, " +
      "ReactJS, Bootstrap, and NodeJS. Modified UI screens and built responsive " +
      "front-end systems, reusable web components, layouts, positioning, media " +
      "queries, and CSS behaviors.",
  },
  {
    label: "Security Analyst",
    value:
      "Cybersecurity Analyst with experience in information security, " +
      "penetration testing, threat hunting, incident response, application " +
      "security, vulnerability assessment, SIEM monitoring, network security, " +
      "Linux, Wireshark, and Python. Investigated security events during a " +
      "six-month internship, documented 12 vulnerabilities, reduced remediation " +
      "time by 30%, and built security monitoring tools. Bachelor degree in " +
      "cybersecurity.",
  },
];

export const REPORT_INCLUDES = [
  "Profile quality score",
  "Detected technical skills",
  "ML category prediction",
  "Focused action plan",
];

export const STATUS_STYLES = {
  Good: "border-[#BBF7D0] bg-[#F0FDF4] text-[#166534]",
  Warning: "border-[#FDE68A] bg-[#FFFBEB] text-[#B45309]",
  "Needs Work": "border-[#FECACA] bg-[#FEF2F2] text-[#B91C1C]",
  Strong: "border-[#BBF7D0] bg-[#F0FDF4] text-[#166534]",
  Moderate: "border-[#FDE68A] bg-[#FFFBEB] text-[#B45309]",
};

export const PRIORITY_STYLES = {
  High: "border-[#FECACA] bg-[#FEF2F2] text-[#B91C1C]",
  Medium: "border-[#FDE68A] bg-[#FFFBEB] text-[#B45309]",
  Low: "border-[#BBF7D0] bg-[#F0FDF4] text-[#166534]",
};
