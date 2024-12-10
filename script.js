// script.js
let currentScene = null;
let storyData = null;
let sceneDetails = {};

document.addEventListener('DOMContentLoaded', function() {
    const importBtn = document.getElementById('importBtn');
    const fileInput = document.getElementById('fileInput');
    const modalOverlay = document.getElementById('modalOverlay');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const sceneTitleEl = document.getElementById('sceneTitle');
    const sceneDescriptionEl = document.getElementById('sceneDescription');
    const sceneChoicesEl = document.getElementById('sceneChoices');

    const editSceneBtn = document.getElementById('editSceneBtn');
    const deleteSceneBtn = document.getElementById('deleteSceneBtn');
    const addChoiceBtn = document.getElementById('addChoiceBtn');
    const sceneEditor = document.getElementById('sceneEditor');
    const sceneIdInput = document.getElementById('sceneIdInput');
    const sceneDescInput = document.getElementById('sceneDescInput');
    const sceneColorInput = document.getElementById('sceneColorInput');
    const saveSceneBtn = document.getElementById('saveSceneBtn');
    const cancelEditBtn = document.getElementById('cancelEditBtn');

    importBtn.addEventListener('click', () => {
      fileInput.click();
    });

    fileInput.addEventListener('change', handleFileSelect);

    closeModalBtn.addEventListener('click', () => {
      modalOverlay.style.display = 'none';
      d3.select("#graphContainer svg").remove();
      sceneTitleEl.innerHTML = '';
      sceneDescriptionEl.innerHTML = '';
      sceneChoicesEl.innerHTML = '';
      currentScene = null;
    });

    editSceneBtn.addEventListener('click', () => {
        if (currentScene && storyData[currentScene]) {
            sceneEditor.style.display = 'block';
            // Populate fields
            sceneIdInput.value = currentScene;
            const desc = storyData[currentScene]?.description?.text || '';
            const color = storyData[currentScene]?.description?.color || 'white';
            sceneDescInput.value = desc;
            sceneColorInput.value = color;
        }
    });

    cancelEditBtn.addEventListener('click', () => {
        sceneEditor.style.display = 'none';
    });

    saveSceneBtn.addEventListener('click', () => {
        if (!currentScene || !storyData[currentScene]) return;
        const oldId = currentScene;
        const newId = sceneIdInput.value.trim();
        const newDesc = sceneDescInput.value.trim();
        const newColor = sceneColorInput.value;

        if (newId !== oldId) {
            // Rename scene key
            storyData[newId] = storyData[oldId];
            delete storyData[oldId];

            // Update all references
            Object.values(storyData).forEach(scene => {
                if (scene.choices) {
                    scene.choices.forEach(choice => {
                        if (choice.next_scene === oldId) {
                            choice.next_scene = newId;
                        }
                        if (choice.success === oldId) {
                            choice.success = newId;
                        }
                        if (choice.failure === oldId) {
                            choice.failure = newId;
                        }
                        if (choice.voting_system && choice.voting_system.options) {
                            choice.voting_system.options.forEach(opt => {
                                if (opt.scene === oldId) opt.scene = newId;
                            });
                        }
                        if (choice.requires_vote) {
                            if (choice.requires_vote.success_scene === oldId) {
                                choice.requires_vote.success_scene = newId;
                            }
                            if (choice.requires_vote.failure_scene === oldId) {
                                choice.requires_vote.failure_scene = newId;
                            }
                        }
                    });
                }
            });
            currentScene = newId;
        }

        // Update scene description
        storyData[currentScene].description = {
            text: newDesc,
            color: newColor
        };

        // Recreate graph and update details
        d3.select("#graphContainer svg").remove();
        createGraph(storyData);
        sceneEditor.style.display = 'none';
        showSceneDetails(currentScene, sceneDetails[currentScene]);
    });

    deleteSceneBtn.addEventListener('click', () => {
        if (currentScene && storyData[currentScene]) {
            if (confirm(`Are you sure you want to delete scene "${currentScene}"?`)) {
                delete storyData[currentScene];

                // Remove references to this scene
                Object.values(storyData).forEach(scene => {
                    if (scene.choices) {
                        scene.choices = scene.choices.filter(choice =>
                            choice.next_scene !== currentScene &&
                            choice.success !== currentScene &&
                            choice.failure !== currentScene &&
                            !(choice.voting_system && choice.voting_system.options && choice.voting_system.options.some(o => o.scene === currentScene)) &&
                            !(choice.requires_vote && 
                              (choice.requires_vote.success_scene === currentScene ||
                               choice.requires_vote.failure_scene === currentScene))
                        );
                        // Also update voting_system/options if needed
                        scene.choices.forEach(choice => {
                            if (choice.voting_system && choice.voting_system.options) {
                                choice.voting_system.options = choice.voting_system.options.filter(o => o.scene !== currentScene);
                            }
                        });
                    }
                });

                d3.select("#graphContainer svg").remove();
                createGraph(storyData);
                showSceneDetails(null, null);
                currentScene = null;
            }
        }
    });

    addChoiceBtn.addEventListener('click', () => {
        if (currentScene && storyData[currentScene]) {
            const choice = {
                text: "New Choice",
                next_scene: ""
            };

            if (!storyData[currentScene].choices) {
                storyData[currentScene].choices = [];
            }

            storyData[currentScene].choices.push(choice);
            d3.select("#graphContainer svg").remove();
            createGraph(storyData);
            showSceneDetails(currentScene, sceneDetails[currentScene]);
        }
    });

    async function handleFileSelect(event) {
      const file = event.target.files[0];
      if(!file) return;

      try {
          const text = await file.text();
          storyData = JSON.parse(text);

          // Validate structure
          if (typeof storyData !== 'object') {
              alert("Invalid story format: Must be an object");
              return;
          }

          const scenes = Object.keys(storyData).filter(k => k !== 'config');
          if (scenes.length === 0) {
              alert("Invalid story format: No scenes found");
              return;
          }

          modalOverlay.style.display = 'block';
          createGraph(storyData);

      } catch (err) {
          console.error('File Read Error:', err);
          alert("Error reading file: " + err.message);
      }
    }

    function createGraph(data) {
      const {nodes, links, sceneDetails: detailsMap} = parseStoryData(data);
      sceneDetails = detailsMap;

      const width = document.getElementById('graphContainer').clientWidth;
      const height = document.getElementById('graphContainer').clientHeight;

      const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width/2,height/2));

      const svgContainer = d3.select("#graphContainer")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

      const svg = svgContainer
        .call(d3.zoom().on("zoom", (event)=> {
          svg.attr("transform", event.transform);
        }))
        .append("g");

      // Arrow marker
      svg.append("defs").append("marker")
          .attr("id", "arrowhead")
          .attr("viewBox", "0 -5 10 10")
          .attr("refX", 25)
          .attr("refY", 0)
          .attr("markerWidth", 6)
          .attr("markerHeight", 6)
          .attr("orient", "auto")
          .append("path")
          .attr("d", "M0,-5L10,0L0,5")
          .attr("fill", "#999");

      const startNode = nodes.find(n => n.id === "start") || nodes[0];
      if (startNode) {
          startNode.fx = width / 2;
          startNode.fy = height / 4; 
          startNode.isStart = true;
      }

      const defs = svg.append("defs");

      defs.append("radialGradient")
          .attr("id", "normalGradient")
          .attr("cx", "30%")
          .attr("cy", "30%")
          .selectAll("stop")
          .data([
              {offset: "0%", color: "#88c9a1"},
              {offset: "100%", color: "#569e7c"}
          ])
          .join("stop")
          .attr("offset", d => d.offset)
          .attr("stop-color", d => d.color);

      defs.append("radialGradient")
          .attr("id", "startGradient")
          .selectAll("stop")
          .data([
              {offset: "0%", color: "#ffd700"},
              {offset: "100%", color: "#ffa500"}
          ])
          .join("stop")
          .attr("offset", d => d.offset)
          .attr("stop-color", d => d.color);

      defs.append("radialGradient")
          .attr("id", "invalidGradient")
          .selectAll("stop")
          .data([
              {offset: "0%", color: "#ff8888"},
              {offset: "100%", color: "#ff4444"}
          ])
          .join("stop")
          .attr("offset", d => d.offset)
          .attr("stop-color", d => d.color);

      // Links
      const link = svg.append("g")
          .selectAll("path")
          .data(links)
          .join("path")
          .attr("class", d => `link ${d.invalid ? 'invalid' : ''}`)
          .attr("marker-end", "url(#arrowhead)")
          .style("stroke", d => {
              if (d.invalid) return "#ff4444";
              if (d.type === "combat") return "#ff8844";
              if (d.type === "voting") return "#44ff44";
              if (d.type === "requires_vote") return "#4444ff";
              return "#999";
          })
          .style("stroke-width", 2)
          .style("fill", "none");

      const node = svg.append("g")
          .selectAll("g")
          .data(nodes)
          .join("g")
          .attr("class", "node-group")
          .call(drag(simulation))
          .on("click", (event, d) => {
              node.selectAll("circle.node").classed("highlighted", false);
              d3.select(event.currentTarget).select("circle.node").classed("highlighted", true);
              showSceneDetails(d.id, sceneDetails[d.id]);
          });

      node.append("circle")
          .attr("r", 18)
          .attr("fill", "white")
          .attr("class", "node-background");

      node.append("circle")
          .attr("r", 15)
          .attr("fill", d => {
              if (d.invalid) return "url(#invalidGradient)";
              if (d.isStart) return "url(#startGradient)";
              return "url(#normalGradient)";
          })
          .attr("class", d => `node ${d.invalid ? 'invalid' : ''} ${d.isStart ? 'start' : ''}`)
          .attr("stroke", "#fff")
          .attr("stroke-width", 2);

      const label = node.append("text")
          .attr("dy", ".35em")
          .attr("text-anchor", "middle")
          .attr("font-size", "12px")
          .attr("font-weight", "bold")
          .attr("fill", "#333")
          .attr("pointer-events", "none")
          .text(d => d.id)
          .each(function(d) {
              const bbox = this.getBBox();
              const padding = 2;
              d3.select(this.parentNode)
                  .insert("rect", "text")
                  .attr("x", bbox.x - padding)
                  .attr("y", bbox.y - padding)
                  .attr("width", bbox.width + (padding * 2))
                  .attr("height", bbox.height + (padding * 2))
                  .attr("fill", "white")
                  .attr("fill-opacity", 0.8)
                  .attr("pointer-events", "none");
          });

      simulation.on("tick", () => {
          link.attr("d", d => {
              const dx = d.target.x - d.source.x;
              const dy = d.target.y - d.source.y;
              const dr = Math.sqrt(dx * dx + dy * dy) * 2;
              return `M${d.source.x},${d.source.y}A${dr},${dr} 0 0,1 ${d.target.x},${d.target.y}`;
          });

          node.attr("transform", d => `translate(${d.x},${d.y})`);
      });

      // Legend
      const legend = svg.append("g")
          .attr("class", "legend")
          .attr("transform", `translate(${width - 150}, 20)`);

      const legendData = [
          { color: "url(#startGradient)", text: "Start Scene" },
          { color: "#ff8844", text: "Combat" },
          { color: "#44ff44", text: "Voting" },
          { color: "#4444ff", text: "Requires Vote" },
          { color: "#ff4444", text: "Invalid Scene" }
      ];

      legend.selectAll("g")
          .data(legendData)
          .join("g")
          .attr("transform", (d, i) => `translate(0, ${i * 25})`)
          .call(g => {
              g.append("rect")
                  .attr("width", 15)
                  .attr("height", 15)
                  .attr("fill", d => d.color);
              g.append("text")
                  .attr("x", 20)
                  .attr("y", 12)
                  .text(d => d.text);
          });

      // Search input
      const searchInput = document.createElement('input');
      searchInput.type = 'text';
      searchInput.placeholder = 'Search scenes...';
      searchInput.style.position = 'absolute';
      searchInput.style.top = '50px';
      searchInput.style.left = '10px';
      searchInput.style.padding = '5px';
      searchInput.style.zIndex = '1000';
      document.getElementById('graphContainer').appendChild(searchInput);

      // Filter invalid scenes
      const filterContainer = document.createElement('div');
      filterContainer.style.position = 'absolute';
      filterContainer.style.top = '90px';
      filterContainer.style.left = '10px';
      filterContainer.style.zIndex = '1000';
      filterContainer.innerHTML = `
          <label style="display: flex; align-items: center; background: rgba(255,255,255,0.95); padding: 8px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
              <input type="checkbox" id="hideInvalidScenes" style="margin-right: 8px;">
              Hide Invalid Scenes
          </label>
      `;
      document.getElementById('graphContainer').appendChild(filterContainer);

      function updateVisibility() {
          const hideInvalid = document.getElementById('hideInvalidScenes').checked;
          node.style("display", d => hideInvalid && d.invalid ? "none" : null);

          link.style("display", d => {
              if (hideInvalid && d.invalid) return "none";
              const sourceVisible = node.filter(n => n.id === d.source.id).style("display") !== "none";
              const targetVisible = node.filter(n => n.id === d.target.id).style("display") !== "none";
              return (hideInvalid && (!sourceVisible || !targetVisible)) ? "none" : null;
          });
      }

      document.getElementById('hideInvalidScenes').addEventListener('change', updateVisibility);

      searchInput.addEventListener('input', (e) => {
          const searchTerm = e.target.value.toLowerCase();
          const hideInvalid = document.getElementById('hideInvalidScenes').checked;
          
          node.each(function(d) {
              const element = d3.select(this);
              const matches = d.id.toLowerCase().includes(searchTerm);
              const shouldShow = matches && (!hideInvalid || !d.invalid);
              element.style("display", shouldShow || (!hideInvalid && !matches) ? null : "none")
                  .select("circle.node")
                  .classed("highlighted", matches)
                  .attr("r", matches ? 20 : 15);
          });

          label.style("opacity", d => 
              searchTerm === '' || d.id.toLowerCase().includes(searchTerm) ? 1 : 0.2
          );

          link.style("display", d => {
              const sourceVisible = node.filter(n => n.id === d.source.id).style("display") !== "none";
              const targetVisible = node.filter(n => n.id === d.target.id).style("display") !== "none";
              if (hideInvalid && d.invalid) return "none";
              return (sourceVisible && targetVisible) ? null : "none";
          });
      });

      // Zoom controls
      const zoomControls = document.createElement('div');
      zoomControls.style.position = 'absolute';
      zoomControls.style.bottom = '20px';
      zoomControls.style.right = '20px';
      zoomControls.style.zIndex = '1000';
      zoomControls.innerHTML = `
          <button style="padding: 5px 10px; margin: 2px; cursor: pointer" id="zoomIn">+</button>
          <button style="padding: 5px 10px; margin: 2px; cursor: pointer" id="zoomReset">Reset</button>
          <button style="padding: 5px 10px; margin: 2px; cursor: pointer" id="zoomOut">-</button>
      `;
      document.getElementById('graphContainer').appendChild(zoomControls);

      const zoom = d3.zoom()
          .scaleExtent([0.1, 4])
          .on("zoom", (event) => {
              svg.attr("transform", event.transform);
          });

      d3.select("#graphContainer svg").call(zoom);

      document.getElementById('zoomIn').onclick = () => {
          d3.select("#graphContainer svg")
              .transition()
              .call(zoom.scaleBy, 1.3);
      };

      document.getElementById('zoomOut').onclick = () => {
          d3.select("#graphContainer svg")
              .transition()
              .call(zoom.scaleBy, 0.7);
      };

      document.getElementById('zoomReset').onclick = () => {
          d3.select("#graphContainer svg")
              .transition()
              .call(zoom.transform, d3.zoomIdentity);
      };
    }

    function drag(simulation) {
      return d3.drag()
        .on("start", function(event, d) {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x; d.fy = d.y;
        })
        .on("drag", function(event,d) {
          d.fx = event.x; d.fy = event.y;
        })
        .on("end", function(event,d) {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null; d.fy = null;
        });
    }

    function showSceneDetails(sceneId, details) {
        currentScene = sceneId;
        if(!details) {
            sceneTitleEl.textContent = "No details available";
            sceneDescriptionEl.textContent = "";
            sceneChoicesEl.textContent = "";
            return;
        }

        const title = details.title || sceneId;
        const desc = details.descriptionText || "";
        const scene = storyData[sceneId];
        let descColor = 'white';
        if (scene && scene.description && scene.description.color) {
            descColor = scene.description.color;
        }

        sceneTitleEl.innerHTML = `<h3>${title}</h3>`;
        sceneDescriptionEl.innerHTML = `<p>${desc}</p>`;
        
        const choices = scene.choices || [];

        if(choices.length > 0) {
            let html = "<ul class='choices-list'>";
            for(let i = 0; i < choices.length; i++) {
                const choice = choices[i];
                const availableScenes = Object.keys(storyData).filter(k => k !== 'config');
                
                // Determine choice type for display
                const isCombat = !!choice.combat;
                const isVoting = !!choice.voting_system;
                const isRequiresVote = !!choice.requires_vote;
                const isBasic = !isCombat && !isVoting && !isRequiresVote;

                // Start building the choice item
                html += `
                    <li data-index="${i}">
                        <div style="margin-bottom:10px;">
                            <label>Choice Text:</label><br/>
                            <input type="text" class="choice-text-input" value="${choice.text}" style="width:90%" />
                        </div>

                        <div style="margin-bottom:10px;">
                            <strong>Choice Type:</strong><br/>
                            <label><input type="radio" name="choice_type_${i}" value="basic" ${isBasic?'checked':''}>Basic</label><br/>
                            <label><input type="radio" name="choice_type_${i}" value="combat" ${isCombat?'checked':''}>Combat</label><br/>
                            <label><input type="radio" name="choice_type_${i}" value="voting" ${isVoting?'checked':''}>Voting</label><br/>
                            <label><input type="radio" name="choice_type_${i}" value="requires_vote" ${isRequiresVote?'checked':''}>Requires Vote</label>
                        </div>

                        <div class="choice-fields-basic" style="${isBasic?'display:block':'display:none'}; margin-bottom:10px;">
                            <label>Next Scene:</label>
                            <select class="choice-nextscene-select">
                                <option value="">(none)</option>
                                ${availableScenes.map(s => `<option value="${s}" ${choice.next_scene===s?'selected':''}>${s}</option>`).join('')}
                            </select>
                        </div>

                        <div class="choice-fields-combat" style="${isCombat?'display:block':'display:none'}; margin-bottom:10px;">
                            <label>Enemy Name:</label><input type="text" class="combat-name" value="${choice.combat?.name||''}"><br/>
                            <label>Enemy Health:</label><input type="number" class="combat-health" value="${choice.combat?.health||50}"><br/>
                            <label>Enemy Attack:</label><input type="number" class="combat-attack" value="${choice.combat?.attack||10}"><br/>
                            <label>Enemy Defense:</label><input type="number" class="combat-defense" value="${choice.combat?.defense||5}"><br/>
                            <label>Enemy Color:</label>
                            <select class="combat-color">
                                ${['black','red','green','yellow','blue','magenta','cyan','white'].map(c => `<option value="${c}" ${(choice.combat?.color===c)?'selected':''}>${c}</option>`).join('')}
                            </select><br/>
                            <label>Success Scene:</label>
                            <select class="combat-success">
                                <option value="">(none)</option>
                                ${availableScenes.map(s => `<option value="${s}" ${choice.success===s?'selected':''}>${s}</option>`).join('')}
                            </select><br/>
                            <label>Failure Scene:</label>
                            <select class="combat-failure">
                                <option value="">(none)</option>
                                ${availableScenes.map(s => `<option value="${s}" ${choice.failure===s?'selected':''}>${s}</option>`).join('')}
                            </select>
                        </div>

                        <div class="choice-fields-voting" style="${isVoting?'display:block':'display:none'}; margin-bottom:10px;">
                            <p>Voting Options:</p>
                            <div class="voting-options-container">
                                ${(choice.voting_system && choice.voting_system.options ? choice.voting_system.options : []).map((opt,optIndex) => `
                                    <div class="voting-option" data-opt-index="${optIndex}">
                                        <label>Option Text:</label><input type="text" class="voting-option-text" value="${opt.text||''}" style="width:200px;">
                                        <label>Scene:</label>
                                        <select class="voting-option-scene">
                                            <option value="">(none)</option>
                                            ${availableScenes.map(s => `<option value="${s}" ${opt.scene===s?'selected':''}>${s}</option>`).join('')}
                                        </select>
                                        <button class="remove-voting-option-btn delete-btn" style="margin-left:5px;">X</button>
                                    </div>
                                `).join('')}
                            </div>
                            <button class="add-voting-option-btn add-btn">Add Voting Option</button><br/><br/>
                            <label>Tie Breaker:</label>
                            <select class="voting-tiebreaker">
                                <option value="random" ${(choice.voting_system?.tie_breaker==='random')?'selected':''}>random</option>
                            </select>
                        </div>

                        <div class="choice-fields-requiresvote" style="${isRequiresVote?'display:block':'display:none'}; margin-bottom:10px;">
                            <label>Min Players:</label><input type="number" class="reqvote-min" value="${choice.requires_vote?.min_players||2}"><br/>
                            <label>Timeout:</label><input type="number" class="reqvote-timeout" value="${choice.requires_vote?.timeout||2}"><br/>
                            <label>Success Scene:</label>
                            <select class="reqvote-success">
                                <option value="">(none)</option>
                                ${availableScenes.map(s => `<option value="${s}" ${choice.requires_vote?.success_scene===s?'selected':''}>${s}</option>`).join('')}
                            </select><br/>
                            <label>Failure Scene:</label>
                            <select class="reqvote-failure">
                                <option value="">(none)</option>
                                ${availableScenes.map(s => `<option value="${s}" ${choice.requires_vote?.failure_scene===s?'selected':''}>${s}</option>`).join('')}
                            </select>
                        </div>

                        <div class="effect-fields" style="margin-bottom:10px;">
                            <p>Effects (optional):</p>
                            <label>Heal:</label><input type="number" class="effect-heal" value="${choice.effect?.heal||''}"><br/>
                            <label>Damage:</label><input type="number" class="effect-damage" value="${choice.effect?.damage||''}"><br/>
                            <label>Buff Attack:</label><input type="number" class="effect-buff-attack" value="${choice.effect?.buff_attack||''}"><br/>
                            <label>Buff Defense:</label><input type="number" class="effect-buff-defense" value="${choice.effect?.buff_defense||''}">
                        </div>

                        <button class="save-choice-btn edit-btn">Save Choice</button>
                        <button class="delete-choice-btn delete-btn">Delete Choice</button>
                    </li>
                `;
            }
            html += "</ul>";
            sceneChoicesEl.innerHTML = html;

            // Add event listeners
            sceneChoicesEl.querySelectorAll('.delete-choice-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const li = e.target.closest('li');
                    const index = parseInt(li.dataset.index);
                    if (confirm("Are you sure you want to delete this choice?")) {
                        storyData[currentScene].choices.splice(index, 1);
                        d3.select("#graphContainer svg").remove();
                        createGraph(storyData);
                        showSceneDetails(currentScene, sceneDetails[currentScene]);
                    }
                });
            });

            sceneChoicesEl.querySelectorAll('.save-choice-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const li = e.target.closest('li');
                    const index = parseInt(li.dataset.index);
                    const choice = storyData[currentScene].choices[index];

                    // Extract updated values
                    const text = li.querySelector('.choice-text-input').value;

                    const typeVal = Array.from(li.querySelectorAll(`input[name="choice_type_${index}"]`)).find(r => r.checked).value;
                    
                    // Reset fields on choice object
                    delete choice.combat;
                    delete choice.voting_system;
                    delete choice.requires_vote;
                    delete choice.next_scene;
                    delete choice.success;
                    delete choice.failure;
                    delete choice.effect;

                    if (typeVal === 'basic') {
                        const nextScene = li.querySelector('.choice-nextscene-select').value.trim();
                        if (nextScene) choice.next_scene = nextScene;
                    } else if (typeVal === 'combat') {
                        const cName = li.querySelector('.combat-name').value.trim();
                        const cHealth = parseInt(li.querySelector('.combat-health').value.trim())||50;
                        const cAttack = parseInt(li.querySelector('.combat-attack').value.trim())||10;
                        const cDefense = parseInt(li.querySelector('.combat-defense').value.trim())||5;
                        const cColor = li.querySelector('.combat-color').value;
                        const cSuccess = li.querySelector('.combat-success').value.trim();
                        const cFailure = li.querySelector('.combat-failure').value.trim();
                        choice.combat = {
                            health: cHealth,
                            attack: cAttack,
                            defense: cDefense
                        };
                        if (cName) choice.combat.name = cName;
                        if (cColor) choice.combat.color = cColor;
                        if (cSuccess) choice.success = cSuccess;
                        if (cFailure) choice.failure = cFailure;
                    } else if (typeVal === 'voting') {
                        const votingOptions = [];
                        li.querySelectorAll('.voting-option').forEach(optEl => {
                            const voText = optEl.querySelector('.voting-option-text').value.trim();
                            const voScene = optEl.querySelector('.voting-option-scene').value.trim();
                            if (voText && voScene) {
                                votingOptions.push({ text: voText, scene: voScene });
                            }
                        });
                        const tieBreaker = li.querySelector('.voting-tiebreaker').value;
                        choice.voting_system = {
                            type: "majority",
                            options: votingOptions,
                            tie_breaker: tieBreaker
                        };
                    } else if (typeVal === 'requires_vote') {
                        const minPlayers = parseInt(li.querySelector('.reqvote-min').value.trim())||2;
                        const timeout = parseInt(li.querySelector('.reqvote-timeout').value.trim())||2;
                        const successScene = li.querySelector('.reqvote-success').value.trim();
                        const failureScene = li.querySelector('.reqvote-failure').value.trim();
                        choice.requires_vote = {
                            min_players: minPlayers,
                            timeout: timeout
                        };
                        if (successScene) choice.requires_vote.success_scene = successScene;
                        if (failureScene) choice.requires_vote.failure_scene = failureScene;
                    }

                    // Effects
                    const healVal = li.querySelector('.effect-heal').value.trim();
                    const damageVal = li.querySelector('.effect-damage').value.trim();
                    const buffAttackVal = li.querySelector('.effect-buff-attack').value.trim();
                    const buffDefenseVal = li.querySelector('.effect-buff-defense').value.trim();

                    const effectObj = {};
                    if (healVal) effectObj.heal = parseInt(healVal)||0;
                    if (damageVal) effectObj.damage = parseInt(damageVal)||0;
                    if (buffAttackVal) effectObj.buff_attack = parseInt(buffAttackVal)||0;
                    if (buffDefenseVal) effectObj.buff_defense = parseInt(buffDefenseVal)||0;

                    if (Object.keys(effectObj).length > 0) {
                        choice.effect = effectObj;
                    }

                    choice.text = text;

                    // Update and redraw
                    d3.select("#graphContainer svg").remove();
                    createGraph(storyData);
                    showSceneDetails(currentScene, sceneDetails[currentScene]);
                });
            });

            // Add voting option
            sceneChoicesEl.querySelectorAll('.add-voting-option-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const li = e.target.closest('li');
                    const votingContainer = li.querySelector('.voting-options-container');
                    const availableScenes = Object.keys(storyData).filter(k => k !== 'config');
                    const newOpt = document.createElement('div');
                    newOpt.className = 'voting-option';
                    newOpt.style.marginBottom = '10px';
                    newOpt.innerHTML = `
                        <label>Option Text:</label><input type="text" class="voting-option-text" style="width:200px;">
                        <label>Scene:</label>
                        <select class="voting-option-scene">
                            <option value="">(none)</option>
                            ${availableScenes.map(s => `<option value="${s}">${s}</option>`).join('')}
                        </select>
                        <button class="remove-voting-option-btn delete-btn" style="margin-left:5px;">X</button>
                    `;
                    votingContainer.appendChild(newOpt);
                    newOpt.querySelector('.remove-voting-option-btn').addEventListener('click', () => {
                        newOpt.remove();
                    });
                });
            });

            // Remove voting option
            sceneChoicesEl.querySelectorAll('.remove-voting-option-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.target.closest('.voting-option').remove();
                });
            });

            // Choice type radio change
            sceneChoicesEl.querySelectorAll('input[type="radio"]').forEach(radio => {
                radio.addEventListener('change', (e) => {
                    const li = e.target.closest('li');
                    const typeVal = e.target.value;
                    li.querySelector('.choice-fields-basic').style.display = (typeVal === 'basic') ? 'block' : 'none';
                    li.querySelector('.choice-fields-combat').style.display = (typeVal === 'combat') ? 'block' : 'none';
                    li.querySelector('.choice-fields-voting').style.display = (typeVal === 'voting') ? 'block' : 'none';
                    li.querySelector('.choice-fields-requiresvote').style.display = (typeVal === 'requires_vote') ? 'block' : 'none';
                });
            });

        } else {
            sceneChoicesEl.innerHTML = "<p>No choices available.</p>";
        }
    }

    function parseStoryData(data) {
      const sceneDetails = {};
      const nodes = [];
      const links = [];
      const invalidScenes = new Set();

      const scenes = Object.keys(data).filter(k => k !== 'config');
      const validScenes = new Set(scenes);

      // Check for invalid references
      for (let sceneId of scenes) {
          const scene = data[sceneId];
          const choices = scene.choices || [];
          for (let choice of choices) {
              const checkInvalid = (target) => {
                  if (target && !validScenes.has(target)) {
                      invalidScenes.add(target);
                  }
              };

              if (choice.next_scene) checkInvalid(choice.next_scene);
              if (choice.success) checkInvalid(choice.success);
              if (choice.failure) checkInvalid(choice.failure);
              if (choice.voting_system && choice.voting_system.options) {
                  for (let opt of choice.voting_system.options) {
                      if (opt.scene) checkInvalid(opt.scene);
                  }
              }
              if (choice.requires_vote) {
                  if (choice.requires_vote.success_scene) checkInvalid(choice.requires_vote.success_scene);
                  if (choice.requires_vote.failure_scene) checkInvalid(choice.requires_vote.failure_scene);
              }
          }
      }

      invalidScenes.forEach(sceneId => {
          nodes.push({
              id: sceneId,
              invalid: true
          });
          sceneDetails[sceneId] = {
              title: sceneId,
              descriptionText: "⚠️ Invalid Scene: This scene is referenced but doesn't exist.",
              choices: [],
              invalid: true
          };
      });

      for (let sceneId of scenes) {
          const scene = data[sceneId];
          nodes.push({id: sceneId, invalid: false});
          
          let desc = "";
          if (scene.description) {
              if (typeof scene.description === 'object') {
                  desc = scene.description.text || "";
              } else {
                  desc = scene.description;
              }
          }

          const choices = scene.choices || [];
          const choiceTexts = [];
          
          for (let choice of choices) {
              const cText = choice.text || "No text";
              choiceTexts.push(cText);

              const addLink = (target, type) => {
                  if (!target) return;
                  links.push({
                      source: sceneId,
                      target: target,
                      type: type,
                      invalid: !validScenes.has(target)
                  });
              };

              if (choice.next_scene) addLink(choice.next_scene, 'basic');
              if (choice.combat) {
                  if (choice.success) addLink(choice.success, 'combat');
                  if (choice.failure) addLink(choice.failure, 'combat');
              }
              if (choice.voting_system && choice.voting_system.options) {
                  for (let opt of choice.voting_system.options) {
                      if (opt.scene) addLink(opt.scene, 'voting');
                  }
              }
              if (choice.requires_vote) {
                  if (choice.requires_vote.success_scene) addLink(choice.requires_vote.success_scene, 'requires_vote');
                  if (choice.requires_vote.failure_scene) addLink(choice.requires_vote.failure_scene, 'requires_vote');
              }
          }

          sceneDetails[sceneId] = {
              title: sceneId,
              descriptionText: desc,
              choices: choiceTexts,
              invalid: false
          };
      }

      // Remove duplicates
      const uniqueLinks = [];
      const linkSet = new Set();
      for (let l of links) {
        const key = l.source + "->" + l.target;
        if(!linkSet.has(key)) {
          linkSet.add(key);
          uniqueLinks.push(l);
        }
      }

      return {nodes, links: uniqueLinks, sceneDetails};
    }

    document.getElementById('exportBtn').addEventListener('click', exportJSON);

    function exportJSON() {
        if (!storyData) {
            alert('No story data to export!');
            return;
        }

        // Create a Blob with the JSON data
        const jsonString = JSON.stringify(storyData, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        
        // Create a temporary link element
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'story_export.json';
        
        // Append link to body, click it, and remove it
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Clean up the URL object
        URL.revokeObjectURL(link.href);
    }

});
