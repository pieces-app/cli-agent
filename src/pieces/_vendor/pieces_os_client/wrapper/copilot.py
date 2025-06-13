from typing import TYPE_CHECKING, List, Optional
import queue

from .context import Context
from .basic_identifier.chat import BasicChat
from .streamed_identifiers.conversations_snapshot import ConversationsSnapshot





if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.qgpt_prompt_pipeline import QGPTPromptPipeline
    from pieces._vendor.pieces_os_client.models.qgpt_question_output import QGPTQuestionOutput
    from .client import PiecesClient
    from pieces._vendor.pieces_os_client.models.relevant_qgpt_seeds import RelevantQGPTSeeds


class Copilot:
    """
    A class to interact with the Pieces Copilot SDK for managing conversations and streaming QGPT responses.
    """

    def __init__(self, pieces_client: "PiecesClient"):
        """
        Initializes the Copilot instance.

        Args:
            pieces_client: The client instance to interact with the Pieces API.
        """
        from .websockets.ask_ws import AskStreamWS
        self.pieces_client = pieces_client
        self._on_message_queue = queue.Queue()
        self.ask_stream_ws = AskStreamWS(self.pieces_client, self._on_message_queue.put)
        self.context = Context(pieces_client, self)
        self._chat = None
        self._chat_id = None

    def stream_question(self,
            query: str,
            pipeline: Optional["QGPTPromptPipeline"] = None
            ) -> None:
        """
        Asks a question to the QGPT model and streams the responses.
        by default it will create a new conversation and always use it in the ask.
        You can always change the conversation in copilot.chat = BasicChat(chat_id="YOU ID GOES HERE")

        Args:
            query (str): The question to ask.
            pipeline (Optional[QGPTPromptPipeline]): the pipeline to use.

        Yields:
            QGPTStreamOutput: The streamed output from the QGPT model.
        """
        from pieces._vendor.pieces_os_client.models.qgpt_stream_input import QGPTStreamInput
        from pieces._vendor.pieces_os_client.models.qgpt_relevance_input import QGPTRelevanceInput
        from pieces._vendor.pieces_os_client.models.qgpt_relevance_input_options import QGPTRelevanceInputOptions
        from pieces._vendor.pieces_os_client.models.qgpt_conversation_pipeline import QGPTConversationPipeline
        from pieces._vendor.pieces_os_client.models.qgpt_conversation_pipeline_for_contextualized_code_workstream_dialog import QGPTConversationPipelineForContextualizedCodeWorkstreamDialog
        from pieces._vendor.pieces_os_client.models.qgpt_prompt_pipeline import QGPTPromptPipeline

        if self.context.ltm.is_chat_ltm_enabled:
            pipeline = pipeline or QGPTPromptPipeline(
                conversation=QGPTConversationPipeline(
                    contextualized_code_workstream_dialog=QGPTConversationPipelineForContextualizedCodeWorkstreamDialog()
                )
            )

        self.ask_stream_ws.send_message(
             QGPTStreamInput(
                 conversation=self._chat_id,
                 relevance=QGPTRelevanceInput(
                     application=self.pieces_client.application.id,
                     query=query,
                     model=self.pieces_client.model_id,
                     options=QGPTRelevanceInputOptions(
                         pipeline=pipeline,
                         question=True
                     ),
                     **self.context._get_relevant_dict()
                 ),
             )
         )

    def question(self,
        query:str, 
        relevant_qgpt_seeds: Optional["RelevantQGPTSeeds"] = None,
        pipeline:Optional["QGPTPromptPipeline"]=None
        ) -> "QGPTQuestionOutput":
        """
        Asks a question to the QGPT model and return the responses,
        Note: the question is not a part of any conversation.

        Args:
            query (str): The question to ask.
            relevant_qgpt_seeds (RelevantQGPTSeeds): Context to the model .
            pipeline (Optional[QGPTPromptPipeline]): the pipeline to use.

        returns:
            QGPTQuestionOutput: The streamed output from the QGPT model.
        """
        from pieces._vendor.pieces_os_client.models.qgpt_question_input import QGPTQuestionInput
        from pieces._vendor.pieces_os_client.models.relevant_qgpt_seeds import RelevantQGPTSeeds
        if not relevant_qgpt_seeds:
            relevant_qgpt_seeds = RelevantQGPTSeeds(iterable=[])

        gpt_input = QGPTQuestionInput(
            query = query,
            model = self.pieces_client.model_id,
            application = self.pieces_client.application.id,
            pipeline=pipeline,
            relevant = relevant_qgpt_seeds
        )

        return self.pieces_client.qgpt_api.question(gpt_input)

    def chats(self) -> List[BasicChat]:
        """
        Retrieves a list of all chat identifiers.

        Returns:
            list[BasicChat]: A list of BasicChat instances representing the chat identifiers.
        """
        return [BasicChat(id) for id in BasicChat.identifiers_snapshot().keys()]

    @property
    def chat(self) -> Optional[BasicChat]:
        """
        Gets the current conversation being used in the copilot.

        Returns:
            Optional[BasicChat]: The current chat instance or None if no chat is set.
        """
        return self._chat

    @chat.setter
    def chat(self, chat: Optional[BasicChat]):
        """
        Sets the current conversation to be used in the copilot.

        Args:
            chat (Optional[BasicChat]): The chat instance to set.
            use chat = None if you want to create a new conversation on asking
        """
        self._chat = chat
        self.context.clear(
            _notifiy=False
        )  # clear the context on changing the conversation
        self._chat_id = chat._id if chat else None


    def create_chat(self, name:Optional[str]=None):
        """
            Creates a New Chat and change the current Copilot chat state to the new generated one
        """
        new_conversation = self.pieces_client.conversations_api.conversations_create_specific_conversation(
            seeded_conversation={
                'name': name,
                'type': 'COPILOT',
            }
        )

        ConversationsSnapshot.identifiers_snapshot[new_conversation.id] = new_conversation # Make sure to update the cache
        self.chat = BasicChat(new_conversation.id)

        return self.chat

