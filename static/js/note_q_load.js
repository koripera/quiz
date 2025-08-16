//個別noteページでnote利用するquestionを遅延して読み込む

function Jsearch(){
	let query3 = `{${document.querySelector('input[name="title"]').value}}`

	fetch("/judge_search",
		{method : "POST",
		 headers: {"Content-type":"application/json; charset=utf-8"},
		 body   : JSON.stringify({query3})})

	.then(response=>{
		if(!response.ok){return Promise.reject(new Error(''));}
		return response.json();
	})

	.then(response =>{
		const element = document.querySelector('#result');
		
		for (const i of response.match){
			const newDiv = document.createElement('div');
			newDiv.classList.add("jq");
			newDiv.style="height: 200px;"
			newDiv.dataset.qid = i
			element.appendChild(newDiv);
		}

		const targets = document.querySelectorAll(".jq");
		const observer = new IntersectionObserver((entries, observer) => {
		entries.forEach(entry => {
			if (entry.isIntersecting) {
			  // 要素が画面に表示された場合の処理
			  get(entry.target)
			}
		  });
		}, {
		  threshold: 0.5 // 要素が50%表示されるときに発火
		});

		targets.forEach(target => {
			observer.observe(target);
		});

		Psearch();

		}
	)
}

function Psearch(){
	let query3 = `{${document.querySelector('input[name="title"]').value}}`

	fetch("/phrase_search",
		{method : "POST",
		 headers: {"Content-type":"application/json; charset=utf-8"},
		 body   : JSON.stringify({query3})})

	.then(response=>{
		if(!response.ok){return Promise.reject(new Error(''));}
		return response.json();
	})

	.then(response =>{
		const element = document.querySelector('#result');
		
		for (const i of response.match){
			//console.log(i);
			const newDiv = document.createElement('div');
			newDiv.classList.add("pq");
			newDiv.style="height: 200px;"
			newDiv.dataset.qid = i[0]
			newDiv.dataset.chara = i[1]
			element.appendChild(newDiv);
		}

		const targets = document.querySelectorAll(".pq");
		const observer = new IntersectionObserver((entries, observer) => {
		entries.forEach(entry => {
			if (entry.isIntersecting) {
			  // 要素が画面に表示された場合の処理
			  pget(entry.target)
			}
		  });
		}, {
		  threshold: 0.5 // 要素が50%表示されるときに発火
		});

		targets.forEach(target => {
			observer.observe(target);
		});

		
		}
	)
}


function get(item){
	let id = item.dataset.qid;
	//console.log(id);
	fetch("/judge_get",
		{method : "POST",
		 headers: {"Content-type":"application/json; charset=utf-8"},
		 body   : JSON.stringify({id})})
	 .then(response=>{
		if(!response.ok){return Promise.reject(new Error('エラーです'));}
		return response.text();
	 })
	 .then(response=>{
		const element = item;
		const newnode = document.createElement("div");
		newnode.innerHTML = response;
		element.parentNode.replaceChild(newnode,element);
	 })
}
function pget(item){
	let id = item.dataset.qid;
	let chara = item.dataset.chara;
	fetch("/phrase_get",
		{method : "POST",
		 headers: {"Content-type":"application/json; charset=utf-8"},
		 body   : JSON.stringify({id,chara})})
	 .then(response=>{
		if(!response.ok){return Promise.reject(new Error('エラーです'));}
		return response.text();
	 })
	 .then(response=>{
		const element = item;
		const newnode = document.createElement("div");
		newnode.innerHTML = response;
		element.parentNode.replaceChild(newnode,element);
	 })
}

Jsearch();
   

