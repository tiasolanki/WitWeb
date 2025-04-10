import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import logo from './assets/chatgpt.svg';
import addBtn from './assets/add-30.png';
import sendBtn from './assets/send.svg';
import userIcon from './assets/user-icon.jpg';
import botLogo from './assets/chatgptLogo.svg';
import LoadingBar from './components/LoadingBar';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);
  
  const sendMessage = async (e) => {
    if (e) e.preventDefault();
    if (e && e.key !== "Enter") return;

    const userMessage = inputText.trim();
    if (!userMessage) return;

    setMessages(messages => [...messages, { sender: 'user', text: userMessage, img: userIcon }]);
    setInputText('');

    setIsLoading(true);
    try {
        const response = await fetch('http://127.0.0.1:5000/get-research-papers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ keyword: userMessage, page_range: '1-1', sort_order: 'ASC' }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        console.log('Data received from backend:', data);

        // Display the received research papers
        const formattedMessages = [
          { sender: 'bot', text: "Here are the research papers:", img: botLogo },
          ...data.paper_title.map((title, index) => {
            const author = data.author[index];
            const publication = data.publication[index];
            const url = data.url_of_paper[index];
            const year = data.year[index];
            return {
              sender: 'bot',
              text: `Title: ${title}\nAuthor: ${author}\nPublication: ${publication}\nYear: ${year}\nURL: ${url}`,
              img: botLogo
            };
          })
        ];
        setMessages(messages => [...messages, ...formattedMessages]);

    } catch (error) {
        console.error('Error:', error);
        setMessages(messages => [...messages, { sender: 'bot', text: "Sorry, I couldn't fetch the research papers.", img: botLogo }]);
    } finally {
        setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <div className='sideBar'>
        <div className='upperSide'>
          <div className='upperSideTop'><img src={logo} className='logo'/><span className='brand'>WitWeb</span></div>
          <button className='midBtn'><img src={addBtn} alt="add button" className='addBtn'/>New Chat</button>
          <LoadingBar isLoading={isLoading} />
        </div>
      </div>
      <div className='main'>
        <div className='chats'>
          {messages.map((message, index) => (
            <div key={index} className={`chat ${message.sender}`}>
              <img src={message.img} className='chatImg'/>
              <p className='txt'>
                {message.sender === 'bot' ? 
                  (typeof message.text === 'string' ? message.text.split('\n').map((line, idx) => <React.Fragment key={idx}>{line}<br/></React.Fragment>) : message.text) :
                  message.text
                }
              </p>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>
        <div className='chatFooter'>
          <div className='inp'>
            <input 
              type='text' 
              placeholder='Send a prompt...' 
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && sendMessage(e)}
            /> 
            <button className='send' onClick={(e) => sendMessage(e)}><img src={sendBtn} alt="Send"/></button>
          </div>
          <p>WitWeb - A world where every query is an adventure in geekdom</p>
        </div>
      </div>
    </div>
  );
}

export default App;
