function search(){
	const query1 = document.getElementById('search1').value;
	const query2 = document.getElementById('search2').value;
	fetch("/note_search",
		{method : "POST",
		 headers: {"Content-type":"application/json; charset=utf-8"},
		 body   : JSON.stringify({query1,query2})})

	.then(response=>{
		if(!response.ok){
			return Promise.reject(new Error('エラーです'));
		}
		return response.json();
	})

	.then(response =>{
		const element = document.querySelector('#result');
		element.innerHTML = "";

		for (const e of response.__match){
			const a = document.createElement("a");
			a.classList.add("links_o")
			a.href = response[e].url;
			a.textContent=response[e].name;
			a.target = "_blank";
			element.appendChild(a);	
		}
		for (const e of response.__nomatch){
			const a = document.createElement("a");
			a.classList.add("links_x")
			a.href = response[e].url;
			a.textContent=response[e].name;
			a.target = "_blank";
			element.appendChild(a);	
		}

	})

}

search();
