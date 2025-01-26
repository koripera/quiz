//初期状態のｺﾝﾃﾝﾂ量を計っておく
let allHeight = Math.max(
  document.body.scrollHeight, document.documentElement.scrollHeight,
  document.body.offsetHeight, document.documentElement.offsetHeight,
  document.body.clientHeight, document.documentElement.clientHeight
);

//ｽｸﾛｰﾙ監視のｲﾍﾞﾝﾄに制限をかけるため使用、本当は使いたくない
let clock = 1


//答え合わせ・解説のPOST
function check(Qid,num,answer,p){
	fetch("/check_J",
		{method : "POST",
		 headers: {"Content-type":"application/json; charset=utf-8"},
		 body   : JSON.stringify({Qid:Qid,num:num,answer:answer})})

	.then(response=>{
		if(response.ok)
		{return response.json();}
		else
		{return Promise.reject(new Error('エラーです'));}
		})

	//画面の変更
	.then(response =>{
		//ﾎﾞﾀﾝのﾛｯｸ
		p.parentNode.querySelector('input[name="answer0"]').disabled=true;
		p.parentNode.querySelector('input[name="answer1"]').disabled=true;

		//取得情報の反映
		p.parentNode.parentNode.parentNode.querySelector(".log").innerHTML=response.logg;
		p.parentNode.parentNode.parentNode.querySelector(".result1").innerHTML=response.result1;
		p.parentNode.parentNode.parentNode.querySelector(".result2").innerHTML=response.result2;
		p.parentNode.parentNode.parentNode.querySelector(".Comment").innerHTML=response.Comment;
		})
	}

//除外を行う処理
function remove(Qid,Lid,q){
	fetch("/remove_J",
		{method : "POST",
		 headers: {"Content-type":"application/json; charset=utf-8"},
		 body   : JSON.stringify({Qid:Qid,Lid:Lid})})

	.then(response=>{
		if(response.ok)
		{return response.json();}
		else
		{return Promise.reject(new Error('エラーです'));}
		})

	//画面の変更
	.then(response =>{
		//ﾎﾞﾀﾝのﾛｯｸ
		q.disabled=true;
		})
	}


//非同期読込、追加
function addQ(){
	fetch("/add_J",
		{method : "POST",
		 headers: {"Content-type":"application/json; charset=utf-8"},
		 body   : JSON.stringify({})})

	.then(response=>{
		if(response.ok)
		{return response.text();}
		else
		{return Promise.reject(new Error('エラーです'));}
		})

	.then(response =>{
		const element = document.querySelector('#wrap');
		const createElement = response;
		element.insertAdjacentHTML('beforeend', createElement);
		})
	}

//ｽｸﾛｰﾙを監視、残りが減ったら、ｺﾝﾃﾝﾂ追加
window.addEventListener('scroll', ()=> {

	//早くｽｸﾛｰﾙすると同じﾃﾞｰﾀで重複して更新するので、制限をかけておく、糞
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

//最初の一回分
addQ();
allHeight = Math.max(
document.body.scrollHeight, document.documentElement.scrollHeight,
document.body.offsetHeight, document.documentElement.offsetHeight,
document.body.clientHeight, document.documentElement.clientHeight,
)

