export const questions = [
  {key:'taste', title:'Bạn thích hương vị nào?', choices:['Thơm và chua nhẹ','Cân bằng, dễ uống','Đậm và đắng']},
  {key:'method', title:'Bạn thường pha bằng gì?', choices:['Phin','Pour-over','Máy espresso']},
  {key:'milk', title:'Chiếc tách của bạn có sữa không?', choices:['Uống đen','Với sữa']},
];

export function recommend(answers) {
  if (questions.some(q => !q.choices.includes(answers[q.key]))) throw new Error('Hãy hoàn thành cả ba câu hỏi.');
  const taste = {
    'Thơm và chua nhẹ': ['Thanh sáng, thơm nhẹ', 'Thử Arabica rang sáng đến vừa, thiên hương hoa hoặc trái cây.'],
    'Cân bằng, dễ uống': ['Êm và cân bằng', 'Thử Arabica rang vừa, thiên vị ngọt và hậu vị chocolate.'],
    'Đậm và đắng': ['Đậm đà, tròn vị', 'Thử blend có Robusta hoặc mức rang vừa–đậm. Concept Arabica của MỘC có thể nhẹ hơn gu bạn.'],
  }[answers.taste];
  const methods = {
    'Phin': 'Phin: 20 g cà phê / 90 ml nước, khoảng 92–96°C. Ủ 25 ml trong 30 giây rồi thêm nước; thử mốc 4–5 phút.',
    'Pour-over': 'Pour-over: 15 g cà phê / 240 ml nước, khoảng 90–94°C. Ủ 40 ml trong 30 giây; thử tổng thời gian 2:30–3 phút.',
    'Máy espresso': 'Espresso: 18 g cà phê vào / 36 g ra, thử mốc 25–30 giây. Điều chỉnh cỡ xay theo dòng chảy và vị.',
  };
  const milk = answers.milk === 'Với sữa'
    ? 'Với sữa: thêm ít trước rồi nếm. Vị chocolate và mức rang vừa thường dễ phối; sữa sẽ làm cảm giác chua dịu hơn.'
    : 'Uống đen: nếm khi còn ấm và khi nguội bớt để cảm nhận độ ngọt, độ chua và hậu vị.';
  return {title:taste[0], reason:taste[1], recipe:methods[answers.method], milk};
}
