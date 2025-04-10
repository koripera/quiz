const textarea = document.getElementById('category');

textarea.addEventListener('keydown', function(e) {
  if (e.key === 'Tab') {
    e.preventDefault(); // デフォルトの動作（フォーカス移動）を止める

    const start = this.selectionStart;
    const end = this.selectionEnd;

    // 現在の内容を取得してタブ文字を挿入
    const before = this.value.substring(0, start);
    const after  = this.value.substring(end);
    this.value = before + "\t" + after;

    // カーソル位置をタブの後に移動
    this.selectionStart = this.selectionEnd = start + 1;
  }
});

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
		base();

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
		const sep = document.createElement("hr");
		element.appendChild(sep);
		/*
		for (const e of response.__nomatch){
			const a = document.createElement("a");
			a.classList.add("links_x")
			a.href = response[e].url;
			a.textContent=response[e].name;
			a.target = "_blank";
			element.appendChild(a);	
		}
		*/

	})
}

function set(){
	const query1 = document.getElementById('category').value;

	fetch("/setcategory",
		{method : "POST",
		 headers: {"Content-type":"application/json; charset=utf-8"},
		 body   : JSON.stringify({query1})})

	.then(response=>{
		if(!response.ok){
			return Promise.reject(new Error('エラーです'));
		}
		return response.text();
	})

	.then(response =>{
		base();
	})
}

function base(){
	fetch("/note",
		{method : "POST",
		 headers: {"Content-type":"application/json; charset=utf-8"},
		 body   : JSON.stringify({})})

	.then(response=>{
		if(!response.ok){
			return Promise.reject(new Error('エラーです'));
		}
		return response.text();
	})

	.then(response =>{
		const element = document.querySelector('#result2');
		element.innerHTML = response;
	})
}

base();
