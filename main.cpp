#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <cstdlib>
#include <ctime>

using namespace std;

enum Suit { HEARTS, DIAMONDS, CLUBS, SPADES };
enum Rank { ACE = 1, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK = 11, QUEEN = 12, KING = 13 };

// CLASS CARD
class Card {
private:
    Suit suit;
    Rank rank;
    bool isFaceUp;

public:
    Card(Suit s, Rank r) : suit(s), rank(r), isFaceUp(false) {}

    Suit getSuit() const { return suit; }
    Rank getRank() const { return rank; }
    bool getFaceUp() const { return isFaceUp; }

    void flip() { isFaceUp = !isFaceUp; }
    void setFaceUp(bool state) { isFaceUp = state; }

    string getColor() const {
        if (suit == HEARTS || suit == DIAMONDS) return "RED";
        return "BLACK";
    }

    string toString() const {
        string rStr = to_string(rank);
        if(rank==1) rStr="A"; if(rank==11) rStr="J"; if(rank==12) rStr="Q"; if(rank==13) rStr="K";
        string sStr = (suit==HEARTS?"H":(suit==DIAMONDS?"D":(suit==CLUBS?"C":"S")));
        return rStr + sStr + (isFaceUp ? "(O)" : "(X)");
    }
};

// CLASS DECK
class Deck {
private:
    vector<Card> cards;

public:
    Deck() { initialize(); }

    void initialize() {
        cards.clear();
        for (int s = HEARTS; s <= SPADES; ++s) {
            for (int r = ACE; r <= KING; ++r) {
                cards.push_back(Card(static_cast<Suit>(s), static_cast<Rank>(r)));
            }
        }
    }

    void shuffle() {
        srand(static_cast<unsigned>(time(0)));
        for (int i = cards.size() - 1; i > 0; i--) {
            int j = rand() % (i + 1);
            swap(cards[i], cards[j]);
        }
    }

    Card draw() {
        if (cards.empty()) throw runtime_error("Deck is empty");
        Card topCard = cards.back();
        cards.pop_back();
        return topCard;
    }

    bool isEmpty() const { return cards.empty(); }
    void addCard(Card c) { cards.push_back(c); }
};

// CLASS CARD PILE
class CardPile {
protected:
    vector<Card> cards;

public:
    virtual ~CardPile() {}

    void addCard(Card c) {
        cards.push_back(c);
    }

    void pushCards(const vector<Card>& newCards) {
        cards.insert(cards.end(), newCards.begin(), newCards.end());
    }

    Card removeTop() {
        if (cards.empty()) throw runtime_error("Pile is empty");
        Card top = cards.back();
        cards.pop_back();
        return top;
    }

    vector<Card> popCards(int count) {
        vector<Card> result;
        if (count > cards.size()) return result; // Помилка

        int startIndex = cards.size() - count;
        for (int i = startIndex; i < cards.size(); ++i) {
            result.push_back(cards[i]);
        }

        cards.erase(cards.begin() + startIndex, cards.end());
        return result;
    }

    bool isEmpty() const { return cards.empty(); }

    Card* getTop() {
        if (cards.empty()) return nullptr;
        return &cards.back();
    }

    Card* getCardFromTop(int index) {
        if (index < 0 || index >= cards.size()) return nullptr;
        return &cards[cards.size() - 1 - index];
    }

    int size() const { return cards.size(); }

    virtual bool canAddCard(const Card& cardToAdd) const = 0;
};

// CLASS TABLEAU
class Tableau : public CardPile {
public:
    bool canAddCard(const Card& cardToAdd) const override {
        if (cards.empty()) {
            return cardToAdd.getRank() == KING;
        }
        const Card& topCard = cards.back();
        bool colorCondition = (cardToAdd.getColor() != topCard.getColor());
        bool rankCondition = (topCard.getRank() == cardToAdd.getRank() + 1);
        return colorCondition && rankCondition;
    }

    bool canMoveStack(int count) {
        if (count <= 0 || count > cards.size()) return false;

        int startIndex = cards.size() - count;
        if (!cards[startIndex].getFaceUp()) return false;

        return true;
    }

    void revealTop() {
        if (!cards.empty() && !cards.back().getFaceUp()) {
            cards.back().flip();
        }
    }
};

// CLASS FOUNDATION
class Foundation : public CardPile {
public:
    bool canAddCard(const Card& cardToAdd) const override {
        if (cards.empty()) {
            return cardToAdd.getRank() == ACE;
        }
        const Card& topCard = cards.back();
        return (cardToAdd.getSuit() == topCard.getSuit()) &&
               (cardToAdd.getRank() == topCard.getRank() + 1);
    }
};

// CLASS WASTE & STOCK
class Waste : public CardPile {
public:
    bool canAddCard(const Card& c) const override { return false; } // Гравцю сюди класти не можна
};

class Stock : public CardPile {
public:
    bool canAddCard(const Card& c) const override { return false; }

    void refillFromWaste(Waste& wastePile) {
        if (!this->isEmpty()) return;
        while (!wastePile.isEmpty()) {
            Card c = wastePile.removeTop();
            c.flip(); // Закриваємо
            this->addCard(c);
        }
    }
};

// CLASS GAME (UPDATED)
class Game {
private:
    Deck deck;
    Stock stock;
    Waste waste;
    vector<Foundation> foundations;
    vector<Tableau> tableaus;
    int movesCount;
    bool gameInProgress;

public:
    Game() {
        movesCount = 0;
        gameInProgress = false;
        foundations.resize(4);
        tableaus.resize(7);
    }

    void startGame() {
        movesCount = 0;
        gameInProgress = true;

        stock = Stock();
        waste = Waste();
        for(auto& f : foundations) f = Foundation();
        for(auto& t : tableaus) t = Tableau();

        deck.initialize();
        deck.shuffle();

        for (int i = 0; i < 7; ++i) {
            for (int j = 0; j <= i; ++j) {
                Card c = deck.draw();
                if (j == i) c.flip();
                tableaus[i].addCard(c);
            }
        }
        while (!deck.isEmpty()) {
            stock.addCard(deck.draw());
        }
    }

    void drawCardFromStock() {
        if (stock.isEmpty()) {
            stock.refillFromWaste(waste);
        } else {
            Card c = stock.removeTop();
            c.flip();
            waste.addCard(c);
        }
        movesCount++;
    }

    bool moveCards(int fromPileType, int fromIndex, int toPileType, int toIndex, int numCards = 1) {
        if (!gameInProgress) return false;

        CardPile* source = nullptr;
        CardPile* dest = nullptr;

        if (fromPileType == 0) {
            if (fromIndex < 0 || fromIndex >= 7) return false;
            source = &tableaus[fromIndex];
        } else if (fromPileType == 1) {
             if (fromIndex < 0 || fromIndex >= 4) return false;
             source = &foundations[fromIndex];
        } else if (fromPileType == 2) {
             source = &waste;
             if (numCards != 1) return false;
        } else { return false; }

        if (toPileType == 0) {
             if (toIndex < 0 || toIndex >= 7) return false;
             dest = &tableaus[toIndex];
        } else if (toPileType == 1) {
             if (toIndex < 0 || toIndex >= 4) return false;
             dest = &foundations[toIndex];
             if (numCards != 1) return false;
        } else { return false; }

        if (source->isEmpty()) return false;
        if (source->size() < numCards) return false;

        Card* cardToPlace = source->getCardFromTop(numCards - 1);

        if (cardToPlace == nullptr) return false;
        if (!cardToPlace->getFaceUp()) return false; // Не можна брати закриті карти

        if (dest->canAddCard(*cardToPlace)) {
            vector<Card> movingCards = source->popCards(numCards);
            dest->pushCards(movingCards);

            if (fromPileType == 0) { // Якщо брали з Tableau
                 static_cast<Tableau*>(source)->revealTop();
            }

            movesCount++;
            return true;
        }

        return false;
    }

    const vector<Tableau>& getTableaus() const { return tableaus; }
    const vector<Foundation>& getFoundations() const { return foundations; }
    const Stock& getStock() const { return stock; }
    const Waste& getWaste() const { return waste; }
    int getMoves() const { return movesCount; }

    bool isWin() {
        int total = 0;
        for(auto& f : foundations) total += f.size();
        return total == 52;
    }
};

extern "C" {
    __declspec(dllexport) Game* Game_Create() {
        return new Game();
    }

    __declspec(dllexport) void Game_Start(Game* game) {
        if (game != nullptr) {
            game->startGame();
        }
    }

    __declspec(dllexport) bool Game_Move(Game* game, int fromType, int fromIdx, int toType, int toIdx, int numCards) {
        if (game != nullptr) {
            return game->moveCards(fromType, fromIdx, toType, toIdx, numCards);
        }
        return false;
    }

    __declspec(dllexport) bool Game_GetCard(Game* game, int zoneType, int zoneIdx, int cardIdx,
                                            int* outSuit, int* outRank, bool* outFaceUp) {
        if (game == nullptr) return false;

        CardPile* pile = nullptr;

        if (zoneType == 0) { // Tableau
            if (zoneIdx < 0 || zoneIdx >= 7) return false;
            const auto& tabs = game->getTableaus();
            if (zoneIdx >= tabs.size()) return false;
             pile = (CardPile*)&(game->getTableaus()[zoneIdx]);

        } else if (zoneType == 1) { // Foundation
            if (zoneIdx < 0 || zoneIdx >= 4) return false;
            pile = (CardPile*)&(game->getFoundations()[zoneIdx]);
        } else if (zoneType == 2) { // Waste
            pile = (CardPile*)&(game->getWaste());
        } else if (zoneType == 3) { // Stock
            pile = (CardPile*)&(game->getStock());
        }

        if (pile == nullptr) return false;

        int size = pile->size();
        if (cardIdx < 0 || cardIdx >= size) return false;

        int offset = size - 1 - cardIdx;
        Card* c = pile->getCardFromTop(offset);

        if (c != nullptr) {
            *outSuit = (int)c->getSuit();
            *outRank = (int)c->getRank();
            *outFaceUp = c->getFaceUp();
            return true;
        }
        return false;
    }

    __declspec(dllexport) int Game_GetPileSize(Game* game, int zoneType, int zoneIdx) {
        if (game == nullptr) return 0;

        if (zoneType == 0) return game->getTableaus()[zoneIdx].size();
        if (zoneType == 1) return game->getFoundations()[zoneIdx].size();
        if (zoneType == 2) return game->getWaste().size();
        if (zoneType == 3) return game->getStock().size();
        return 0;
    }

    __declspec(dllexport) void Game_Delete(Game* game) {
        if (game != nullptr) {
            delete game;
        }
    }

    __declspec(dllexport) int Game_GetMoves(Game* game) {
        if (game != nullptr) return game->getMoves();
        return 0;
    }

    __declspec(dllexport) void Game_DrawFromStock(Game* game) {
        if (game != nullptr) {
            game->drawCardFromStock();
        }
    }
    __declspec(dllexport) bool Game_IsWin(Game* game) {
        if (game != nullptr) return game->isWin();
        return false;
    }
}