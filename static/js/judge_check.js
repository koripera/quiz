//答え合わせ・解説のPOST
function check_J(Qid,num,answer,p){
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
