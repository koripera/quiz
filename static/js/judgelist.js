let allHeight = Math.max(
  document.body.scrollHeight, document.documentElement.scrollHeight,
  document.body.offsetHeight, document.documentElement.offsetHeight,
  document.body.clientHeight, document.documentElement.clientHeight
);

let clock = 1
let list  = null 

/*
		for (const i of response.match){
			get(i)
		}
*/

//問題のリストを取得
function search(){
	const query1 = document.getElementById('search1').value;
	const query2 = document.getElementById('search2').value;
	const query3 = document.getElementById('search3').value;

	fetch("/judge_search",
		{method : "POST",
		 headers: {"Content-type":"application/json; charset=utf-8"},
		 body   : JSON.stringify({query1,query2,query3})})

	.then(response=>{
		if(!response.ok){return Promise.reject(new Error('エラーです'));}
		return response.json();
	})

	.then(response =>{
		const element = document.querySelector('#result');
		element.innerHTML = `<div>hit is ${response.match.length}</div>`;
		
		for (const i of response.match){
			const newDiv = document.createElement('div');
			newDiv.classList.add("q");
			newDiv.style="height: 200px;"
			newDiv.dataset.qid = i
			element.appendChild(newDiv);
		}

		const targets = document.querySelectorAll(".q");
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

		}
	)
}

//問題のhtmltextを取得
function get(item){
	let id = item.dataset.qid;
	console.log(id);
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
/*
window.addEventListener('scroll', ()=> {
	//早くｽｸﾛｰﾙすると同じﾃﾞｰﾀで重複して更新するので、制限をかけておく
	clock += 1
	if (clock >= 600){clock=0;}
	if (clock % 20 ==0){	

	//ﾒｲﾝ部分
	if (allHeight - window.innerHeight - window.scrollY <= 1000){
		addQ();
		allHeight = Math.max(
		document.body.scrollHeight, document.documentElement.scrollHeight,
		document.body.offsetHeight, document.documentElement.offsetHeight,
		document.body.clientHeight, document.documentElement.clientHeight,);
		}

		}
	});
*/
search();
