import streamlit as st
# from supervisor_agent_2 import supervisor_agent
# from supervisor_agent_3 import multi_graph
from supervisor_agent_4 import supervisor_agent
from langchain_core.messages.tool import ToolMessage
from langchain_core.messages import AIMessageChunk

st.title("Grocery Seller Agent")
st.subheader("Multi-agent-Langgraph")

if "message_history" not in st.session_state:
    st.session_state['message_history'] = []

if "configurable" not in st.session_state:
    st.session_state['configurable'] = {"configurable": {"thread_id": "uip232"}}

def graph_response_generator(prompt):
    user_msg = {"messages":[{"role": "human", "content" : prompt}]}

    ToolMessage_passed_Flag = False
    Tool_use_Found = False
    
    for response_tuple, metadata in supervisor_agent.stream(user_msg, 
                                                        config= st.session_state['configurable'], 
                                                        stream_mode="messages"):

        if isinstance(response_tuple.content, list) and len(response_tuple.content) > 0:
            if response_tuple.content[0].get("type") == "tool_use":
                Tool_use_Found = True 

            elif not Tool_use_Found and response_tuple.content[0].get("type") == "text":
                # Text_use_Found = True 
                # print("When tool use not found")
                # print(f'{response_tuple= }  {metadata= }'); print()
                yield response_tuple.content[0].get("text","")
           

        if Tool_use_Found:
            if type(response_tuple) == ToolMessage and response_tuple.status == "success":
                ToolMessage_passed_Flag = True 
                # print("Point where tool use found")
                # print(f'{response_tuple= }  {metadata= }'); print()

            if ToolMessage_passed_Flag and type(response_tuple)== AIMessageChunk and isinstance(response_tuple.content, list) and len(response_tuple.content) > 0:
                # print("Found success TOOL USE")
                # print(f'{response_tuple= }  {metadata= }'); print()
                yield response_tuple.content[0].get("text","")

# def graph_response_generator(prompt):
    
#         # for response_tuple in supervisor_agent.stream(
#         #     {'messages': prompt},
#         #     config=st.session_state['configurable'],
#         #     stream_mode="messages",
#         # ):
#         #     if len(response_tuple) > 0 and isinstance(response_tuple[0].content, list):
#         #         if len(response_tuple[0].content) > 0:
#         #             content_item = response_tuple[0].content[0]
#         #             if isinstance(content_item, dict):
#         #                 yield content_item.get("text", "")
        
#     GOTO_FINISH_FLAG = False
#     for repsonse_tupple in supervisor_agent.stream({'messages': prompt}, 
#                                             config= st.session_state['configurable'], 
#                                             stream_mode="messages",):
#         # print(f'{repsonse_tupple = }'); print()

#         if isinstance(repsonse_tupple[0].content, list):
#             if len(repsonse_tupple[0].content) > 0:
                # print(f'{repsonse_tupple[0].content = }'); print()
                # if (repsonse_tupple[0].content[0].get("type","") == "tool_use") and (repsonse_tupple[1]['langgraph_triggers'][0] == "branch:to:supervisor"):
                #     yield repsonse_tupple[0].content[0].get("input","")
                # if repsonse_tupple[1].get("langgraph_node") == "goto_decider":
                #     # print(repsonse_tupple); print() 
                
                # repsonse_tupple[0].content = [{'type': 'text', 'text': 'FINISH', 'index': 0}]
                # if repsonse_tupple[0].content[0].get("text") == "FINISH":
                #     print('We got finish')
                #     print(repsonse_tupple); print()
                #     GOTO_FINISH_FLAG = True
                    
                # if GOTO_FINISH_FLAG:
                #     if repsonse_tupple[1].get("langgraph_node") == "supervisor_message":
                #         print(repsonse_tupple); print()
                #         yield repsonse_tupple[0].content[0].get("text","")
                # if repsonse_tupple[1].get("langgraph_node") == "supervisor_message":
                #     # print(repsonse_tupple); print()
                #     yield repsonse_tupple[0].content[0].get("text","")
    
    

        
# def graph_response_generator(prompt):
#     for repsonse_tupple in supervisor_agent.stream({'messages': prompt}, 
#                                              config= st.session_state['configurable'], 
#                                              stream_mode="messages",):
#         # print(prompt)
#         # print()
#         if isinstance(repsonse_tupple[0].content, list):
#             if len(repsonse_tupple[0].content) > 0:
#                   if repsonse_tupple[1].get("langgraph_node") == "agent":
#                 #     # print(repsonse_tupple); print()
#                     yield repsonse_tupple[0].content[0].get("text","")
                #   yield repsonse_tupple[0].content[0].get("text","")
      

for message_dict in st.session_state['message_history']:
    with st.chat_message(name= message_dict['role']):
        st.markdown(message_dict['content'])

if prompt := st.chat_input("Bol na bhai..."):
    # print(f"{prompt = }n")

    st.session_state['message_history'].append({'role': "user", "content" : prompt})

    st.chat_message(name= "user").markdown(prompt)

    with st.chat_message(name= "assistant"):
        response_tuple = st.write_stream(graph_response_generator(prompt))

    st.session_state['message_history'].append({'role': 'assistant', 'content': response_tuple})