// Minimal client-side logic for assessment flow
(async function(){
  function qs(sel){return document.querySelector(sel)}
  const form = qs('#assessment-form')
  const summary = qs('#summary')
  const scoreValue = qs('#score-value')
  const breakdownDiv = qs('#breakdown')
  const emailForm = qs('#email-form')
  const bookLink = qs('#book-link')

  if(form){
    form.addEventListener('submit', async (e)=>{
      e.preventDefault()
      const data = new FormData(form)
      const payload = {
        organization_name: data.get('organization_name'),
        organization_type: data.get('organization_type'),
        employees: Number(data.get('employees')||0),
        cloud: data.get('cloud'),
        data_sources: (data.get('data_sources')||"").split(',').map(s=>s.trim()).filter(Boolean),
        it_team_size: Number(data.get('it_team_size')||0),
        has_ai: data.get('has_ai') === 'on'
      }
      // Call API
      try{
        const res = await fetch('/api/assess',{
          method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)
        })
        const result = await res.json()
        // show summary
        scoreValue.textContent = result.readiness_score + ' / 100'
        breakdownDiv.innerHTML = '<h4>Breakdown</h4>' + Object.entries(result.breakdown).map(([k,v])=>`<div>${k}: ${v}</div>`).join('')
        summary.hidden = false
        // store token to allow download after email
        summary.dataset.token = result.token
        // set book link to Google Meet + placeholder - user will replace with real scheduling
        const meetUrl = 'https://meet.google.com' // placeholder
        bookLink.href = meetUrl
      }catch(err){
        alert('Error contacting assessment API')
        console.error(err)
      }
    })
  }

  if(emailForm){
    emailForm.addEventListener('submit', async (e)=>{
      e.preventDefault()
      const token = qs('#summary').dataset.token
      const form = new FormData(emailForm)
      const email = form.get('email')
      try{
        const res = await fetch(`/api/claim/${token}`,{
          method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email})
        })
        const data = await res.json()
        if(data.success){
          // Redirect to full report page
          window.location.href = `/assessments/result.html?token=${token}`
        }else{
          alert('Could not claim report')
        }
      }catch(err){
        alert('Error claiming report')
      }
    })
  }

  // On result page, fetch result by token and render
  if(window.location.pathname.endsWith('/assessments/result.html')){
    const params = new URLSearchParams(window.location.search)
    const token = params.get('token')
    if(token){
      try{
        const res = await fetch(`/api/result/${token}`)
        const data = await res.json()
        qs('#score-display').textContent = data.readiness_score + ' / 100'
        const tbody = qs('#breakdown-table tbody')
        tbody.innerHTML = Object.entries(data.breakdown).map(([k,v])=>`<tr><td>${k}</td><td>${v}</td></tr>`).join('')
        qs('#priorities').innerHTML = '<h3>Top 3 Priorities</h3><ol>' + data.top_priorities.map(p=>`<li>${p}</li>`).join('') + '</ol>'
        qs('#roadmap').innerHTML = '<h3>Recommended 90-Day Roadmap</h3><ol><li>Month 1: Fix data foundations</li><li>Month 2: Build integration layer</li><li>Month 3: Deploy first AI workflow</li></ol>'
        qs('#book-architecture').href = 'https://meet.google.com' // Google Meet placeholder
      }catch(err){console.error(err)}
    }
  }
})();
