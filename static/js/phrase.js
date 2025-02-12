//初期状態のｺﾝﾃﾝﾂ量を計っておく
let allHeight = Math.max(
  document.body.scrollHeight, document.documentElement.scrollHeight,
  document.body.offsetHeight, document.documentElement.offsetHeight,
  document.body.clientHeight, document.documentElement.clientHeight
);

//ｽｸﾛｰﾙ監視のｲﾍﾞﾝﾄに制限をかけるため使用
let clock = 1

//非同期読込、追加
function addQ(){
	fetch('/add_P',
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

//最初の一回分
addQ();
allHeight = Math.max(
document.body.scrollHeight, document.documentElement.scrollHeight,
document.body.offsetHeight, document.documentElement.offsetHeight,
document.body.clientHeight, document.documentElement.clientHeight,
)

